import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import nltk
from flask import Flask, render_template,request
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')





df1=pd.read_csv('Fake_News.csv',encoding='windows-1252')

df1

nltk.download('stopwords')

df1.shape

df1.info()

"""DATA PRE-PROCESSING

"""

#checking the missing value
df1.isnull().sum()

#removing the date and summary column
df1.drop(['Date'],axis=1, inplace=True)
df1.drop(['Summary'],axis=1, inplace=True)
df1.head()

#changing the name of Fake/Real(1/0) Fake=1, Real=0 to label
df1=df1.rename(columns={'Fake/Real(1/0)':'label'})
df1.head(5)

#convert all letters to loercase in headlines
df1['Headlines']=df1['Headlines'].apply(lambda x: x.lower())
df1.head(5)

#removing punctuations
import string
def punctuation_removal(text):
  list= [char for char in text if char not in string.punctuation]
  clean=''.join(list)
  return clean

df1['Headlines']=df1['Headlines'].apply(punctuation_removal)
df1.head(5)

#removing the stopword from the data
from nltk.corpus import stopwords
stop=stopwords.words('english')
df1['Headlines']=df1['Headlines'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))

df1.head(5)

"""BASIC DATA EXPLORATION"""

#how many articles per subject
# print(df1.groupby(['Sources'])['Headlines'].count())
# df1.groupby(['Sources'])['Headlines'].count().plot(kind='line')
# #plt.show()

# #how many fake and news articles
# print(df1.groupby(['label'])['Headlines'].count())
# df1.groupby(['label'])['Headlines'].count().plot(kind='bar')
# #plt.show()

"""SPLITTING DTA"""

#separating the data and label
X = df1['Headlines'].values
Y = df1['label'].values

print(X)

print(Y)

df1.isnull().values.any()

df1['label'].isnull().replace(np.nan,0)

#splitting the data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.3 ,stratify=Y, random_state=2)

#converting textual data into numerical data
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english' , max_df=0.4)
tfidf_X_train = vectorizer.fit_transform(X_train)
tfidf_X_test = vectorizer.transform(X_test)
#result=vectorizer.fit_transform(X)

print(tfidf_X_train)

"""PASSIVE AGRESSIVE CLASSIFIER"""

from sklearn.linear_model import PassiveAggressiveClassifier
classifier = PassiveAggressiveClassifier(max_iter=30)
classifier.fit(tfidf_X_train,Y_train)

#accuracy for passive agressive classifier
pred=classifier.predict(tfidf_X_train)
score= accuracy_score(Y_train,pred)
print(f"Accuracy: {round(score*100,2)}%")

#saving the model on pickle module disk
import pickle
pickle.dump(classifier,open('model.pkl','wb'))

#loading model from disk
loaded_model= pickle.load(open('model.pkl','rb'))

"""MAKING A PREDICTVE SYSTEM"""

#predictive System

def fake_news_predict(news):
  input=[news]
  vectorized_input=vectorizer.transform(input)
  prediction=loaded_model.predict(vectorized_input)
  print(prediction)
  if (prediction==0):
    return "Result: The News is Real"
  else:
    return "Result: The News is Fake"



@app.route('/predict', methods =["GET", "POST"])
def predict():
	if request.method == "POST":
		news = request.form.get('news')
		result = fake_news_predict(news)
	return render_template('predict.html',result=result,news=news)