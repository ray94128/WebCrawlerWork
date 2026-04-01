import pandas as pd
from snownlp import SnowNLP
import jieba.analyse
import plotly.express as px
import plotly.graph_objects as go

class ReviewAnalyzer:
    def __init__(self, dataframe):
        self.df = dataframe

    def analyze_sentiment(self):
        """計算每條評論的情緒得分 (0.0 到 1.0)"""
        def get_sentiment(text):
            if not text:
                return 0.5 # 中性
            try:
                s = SnowNLP(text)
                return s.sentiments
            except:
                return 0.5
        
        self.df['sentiment_score'] = self.df['review'].apply(get_sentiment)
        self.df['sentiment_label'] = self.df['sentiment_score'].apply(
            lambda x: '正向' if x > 0.6 else ('負向' if x < 0.4 else '中性')
        )
        return self.df

    def get_keywords(self, sentiment='正向', top_k=10):
        """提取特定情緒評論中的關鍵字"""
        target_reviews = self.df[self.df['sentiment_label'] == sentiment]['review'].tolist()
        text_corpus = " ".join(target_reviews)
        if not text_corpus.strip():
            return []
        
        # 使用 jieba 提取關鍵字 (TF-IDF)
        keywords = jieba.analyse.extract_tags(text_corpus, topK=top_k)
        return keywords

    def plot_sentiment_distribution(self):
        """情緒佔比餅圖"""
        counts = self.df['sentiment_label'].value_counts().reset_index()
        counts.columns = ['sentiment', 'count']
        fig = px.pie(counts, values='count', names='sentiment', 
                     title='評論情緒分佈',
                     color='sentiment',
                     color_discrete_map={'正向':'#2ecc71', '中性':'#f1c40f', '負向':'#e74c3c'})
        return fig

    def plot_rating_distribution(self):
        """星等分佈直方圖"""
        fig = px.histogram(self.df, x='rating', 
                           title='店家星等分佈',
                           labels={'rating': '星等', 'count': '數量'},
                           color_discrete_sequence=['#3498db'])
        fig.update_layout(bargap=0.2)
        return fig

    def plot_sentiment_trend(self):
        """情緒分數分佈散點圖"""
        fig = px.scatter(self.df, y='sentiment_score', x=self.df.index,
                         color='sentiment_label',
                         title='個別評論情緒得分分佈',
                         labels={'y': '情緒得分 (1為最正向)', 'index': '評論編號'})
        return fig
