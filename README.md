# STOCK_PRICE_FINBERT
 The reviews of guba were taken as the initial corpus, and the Finbert model was used to analyze the polarity of Chinese comments and predict the stock rise.
# Project Natures
 The project is mainly composed of crawlers, Finbert model and hypothesis testing.
 
 The crawler technology uses Xpath and Json technology to crawl 20W reviews on the stock bar forum of Oriental Fortune.com.
 
 The Finbert model supports layer-by-layer thawing and accumulation of gradients. At the same time, random segmentation of the data set is used in each epoch, which not only adds  randomness to model training, reduces the risk of overfitting, and can alleviate the problem of small sample size to a certain extent. Finally, the bert model is encapsulated to facilitate future model expansion, and Finbert is given the Sklearn interface.
 
 Hypothesis testing is used to assess the degree of correlation between polarity and stock gains in a certain period of time.
# Use of code
 Click the link below to download the pre-trained bert model and place it in /models/language_model/.
 https://drive.google.com/open?id=1AQitrjbvCWc51SYiLN-cJq4e0WiNN4KY
 
# Issue to be solved
 The scattered topics of social comments make it difficult to clean a large amount of dirty data, which seriously affects the performance of the model.
