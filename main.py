import requests
import redis
import matplotlib.pyplot as plt
import pandas as pd
import json

class APIFetcher:
    """
    Fetches data from a specified API.
    """
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_comments(self):
        """
        Fetches comment data from the API.
        
        Returns:
            List[dict]: A list of comment data in JSON format.
        """
        response = requests.get(f"{self.base_url}")
        return response.json()


class RedisManager:
    """
    Manages interactions with a Redis database.
    """
    
    def __init__(self, host='localhost', port=6379):
        self.db = redis.Redis(host=host, port=port, decode_responses=True)
    
    def insert_data(self, key, data):
        """
        Inserts JSON data into Redis under a specified key, encoding it as a string.
        
        Args:
            key (str): The Redis key.
            data (dict or list): The data to insert, which will be serialized to JSON string.
        """
        self.db.set(key, json.dumps(data))
    
    def retrieve_data(self, key):
        """
        Retrieves and decodes JSON data from Redis for a given key.
        
        Args:
            key (str): The Redis key.
        
        Returns:
            data (list or dict): The JSON data retrieved and deserialized from Redis.
        """
        data = self.db.get(key)
        if data:
            return json.loads(data)
        return None


class ChartGenerator:
    """
    Generates various types of charts from a given dataset and saves them as images.
    """
    
    def __init__(self, data):
        self.data = pd.DataFrame(data)
    
    def line_chart(self, by, column, title, filename):
        """
        Generates a line chart for the average of a specific column, grouped by another column, and saves it as an image.
        
        Args:
            by (str): The column to group by (e.g., 'postId').
            column (str): The column to average and plot (e.g., 'comment_length').
            title (str): The title of the chart.
            filename (str): The filename to save the chart image.
        """
        # Calculate the average of the column grouped by 'by'
        grouped_data = self.data.groupby(by)[column].mean()
        
        plt.figure(figsize=(12, 6))
        grouped_data.plot(kind='line')
        plt.title(title)
        plt.xlabel(by)
        plt.ylabel(f'Average {column}')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    def histogram(self, column, title, filename, bins):
        """
        Generates a histogram for a specific column and saves it as an image.
        
        Args:
            column (str): The column to generate a histogram for.
            title (str): The title of the chart.
            filename (str): The filename to save the chart image.
            bins (int): The number of bins for the histogram.
        """
        self.data[column].apply(len).plot.hist(bins=bins)
        plt.title(title)
        plt.xlabel('Length')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()


class DataAggregator:
    """
    Performs aggregation operations on datasets.
    """
    
    def __init__(self, data):
        self.data = pd.DataFrame(data)
    
    def average_length(self, column):
        """
        Calculates the average length of strings in a given column.
        
        Args:
            column (str): The column to calculate the average length for.
            
        Returns:
            float: The average length of the column's strings.
        """
        return self.data[column].apply(len).mean()


# Usage example
api_url = 'https://jsonplaceholder.typicode.com/comments'
api_fetcher = APIFetcher(api_url)
comments_data = api_fetcher.get_comments()

redis_manager = RedisManager()
redis_key = 'comments_data'
redis_manager.insert_data(redis_key, comments_data)

# Assuming data retrieval for processing
processed_data = redis_manager.retrieve_data(redis_key)

# Adding a temporary column 'comment_length' for boxplot
processed_data = pd.DataFrame(processed_data)
processed_data['comment_length'] = processed_data['body'].apply(len)

chart_generator = ChartGenerator(processed_data)
chart_generator.line_chart('postId', 'comment_length', 'Average Comment Length per Post', 'average_comment_length_per_post.png')
chart_generator.histogram('body', 'Comment Body Length Distribution', 'comment_length_distribution.png', 20)

data_aggregator = DataAggregator(processed_data)
average_comment_length = data_aggregator.average_length('body')
print(f'Average Comment Length: {average_comment_length}')
