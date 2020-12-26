#!/usr/bin/env python
# coding: utf-8

import torch as t
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler,TensorDataset, random_split


class InputExample(object):
    def __init__(self, text, label):
        self.text = text
        self.label = label


class InputFeature(object):
    def __init__(self,input_id,attention_mask,label_id):
        self.input_id = input_id
        self.attention_mask = attention_mask
        self.label_id = label_id

class Tool(object):

    @classmethod
    def get_weight_from_dataset(cls,dataset,lable_ids_list,class_weight):
        if class_weight == 'balanced':
            label_list = t.tensor([dataset[i][2] for i in range(dataset.__len__())]).numpy()
            weight = t.tensor([label_list.size/label_list[label_list == label].size for label in list(lable_ids_list)])
        else:
            weight = t.ones(1,len(lable_ids_list))
        return weight


class Config(object): ### 存储用户指定的要求 数据类
    def __init__(
                self,
                label_map,
                max_seq_length,
                train_batch_size,
                eval_batch_size,
                learning_rate,
                num_train_epochs,
                warm_up_proportion,
                no_cuda,
                do_lower_case,
                seed,
                local_rank,
                gradient_accumulation_steps,
                fp16,
                discriminate,
                gradual_unfreeze,
                encoder_no,
                dft_rate
                ):
        self.label_map = label_map
        self.do_lower_case = do_lower_case
        self.max_seq_length = max_seq_length
        self.train_batch_size = train_batch_size
        self.local_rank = local_rank
        self.eval_batch_size = eval_batch_size
        self.learning_rate = learning_rate
        self.num_train_epochs = num_train_epochs
        self.warm_up_proportion = warm_up_proportion
        self.no_cuda = no_cuda
        self.seed = seed
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.fp16 = fp16
        self.discriminate = discriminate
        self.gradual_unfreeze = gradual_unfreeze
        self.encoder_no = encoder_no
        self.dft_rate = dft_rate


class FinSentProcessor(object):  ### 假设数据已经分好句了  模板拼接一致，但逻辑改变

    def convert_raws2examples(self,raw_data):
        examples = []
        for text,label in raw_data:
            examples.append(InputExample(text,label))
        return examples

    def convert_examples2features(self,examples,tokenizer,max_length,label_map):  ### 得到经过tensor的feautres列表
        features = []
        for ex in examples:
            encoded_dict = tokenizer.encode_plus(  ### 这里可以改进，传参
                                                ex.text,
                                                add_special_tokens = True,
                                                max_length=max_length,
                                                pad_to_max_length = True,
                                                return_attention_mask = True,
                                                return_tensors='pt'
                                                )
            label_id = t.tensor(label_map[ex.label])
            features.append(InputFeature(encoded_dict['input_ids'],encoded_dict['attention_mask'],label_id))
        return features

    def convert_features2dataloader_T_V(self,features,val_batch_size=64,is_train=False,
                                                      train_batch_size=64,rate=0.8,lable_ids_list=[0,1],class_weight='balanced'):
        input_ids = []
        attention_masks = []
        label_ids = []
        for fea in features:
            input_ids.append(fea.input_id)
            attention_masks.append(fea.attention_mask)
            label_ids.append(fea.label_id)

        input_ids = t.cat(input_ids, dim=0)  ### Tensor列表 转成 一个 列表Tensor
        attention_masks = t.cat(attention_masks, dim=0)
        label_ids = t.tensor(label_ids) ### numpy列表 转成 一个Tensor

        data = TensorDataset(input_ids,attention_masks,label_ids)

        if is_train == False: ## 如果在训练的话，根据比例分割数据集，并用不同的batchsize来创建各自的dataloader对象
            sampler_V = SequentialSampler(data)
            dataloader_V = DataLoader(data, sampler=sampler_V, batch_size= val_batch_size)
            return dataloader_V

        train_size = int(rate * len(data))
        val_size = len(data) - train_size
        train_data,val_data = random_split(data,[train_size,val_size])

        sampler_T = RandomSampler(train_data)
        dataloader_T = DataLoader(train_data, sampler=sampler_T, batch_size=train_batch_size)
        weight_T = Tool.get_weight_from_dataset(train_data,lable_ids_list,class_weight)

        my_sampler_V = SequentialSampler(val_data)
        dataloader_V = DataLoader(val_data, sampler=my_sampler_V, batch_size=val_batch_size)
        weight_V = Tool.get_weight_from_dataset(val_data,lable_ids_list,class_weight)

        return dataloader_T,dataloader_V,weight_T,weight_V



  
