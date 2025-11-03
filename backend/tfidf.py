import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
import string
from pymongo import MongoClient  # Import MongoDB client
from transformers import pipeline
import spacy

nltk.download('punkt')
nltk.download('stopwords')


# Step 1: Extract Text from Web Page
def extract_text_from_url_1(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract text from the webpage
    text = ' '.join(p.get_text() for p in soup.find_all('p'))
    return text

# Step 2: Pre-process Text
def preprocess_text(text):
    # Lowercase the text
    text = text.lower()
    
    # Remove punctuation and numbers
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ''.join([char for char in text if not char.isdigit()])
    
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)

# Step 3: Tokenize and Find Number of Sentences
def tokenize_text(text):
    sentences = nltk.sent_tokenize(text)
    words = nltk.word_tokenize(text)
    return sentences, words

# Step 4: Calculate TF-IDF Values
def calculate_tfidf(text):
    vectorizer = TfidfVectorizer()
    
    # Fit the model on the text (we only have one document here)
    tfidf_matrix = vectorizer.fit_transform([text])
    
    # Get the TF-IDF values
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()
    
    # Create a dictionary of words and their scores
    tfidf_dict = dict(zip(feature_names, tfidf_scores))
    
    return tfidf_dict

# Step 5: Sort Results
def sort_tfidf(tfidf_dict):
    sorted_tfidf = sorted(tfidf_dict.items(), key=lambda item: item[1], reverse=True)
    return sorted_tfidf

# Step 6: Return Top N Keywords
def get_top_keywords(sorted_tfidf, top_n=10):
    return sorted_tfidf[:top_n]

# Step 7: Insert into MongoDB
def insert_into_database(url, keywords, summary):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if hosted elsewhere
        db = client["knowledge_base"]
        # collection = db["Annotations"]
        summaries_collection = db["Summaries"]
        
        # Convert the keywords list to a comma-separated string
        keywords_str = ', '.join(keywords)
        
        # Prepare the data to be inserted
        data = {
            "link": url,
            "annotations": keywords_str,
            "summary": summary 
        }
        
        # Insert the data
        summaries_collection.insert_one(data)
        print("Data inserted successfully into MongoDB.")
        
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")
        
        
        
        
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])
    return text[:3000]  # Limit to avoid excessive text

def summarize_text(text):
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']





# url = "https://www.ibm.com/think/topics/artificial-intelligence"  # Replace with your target URL
urls_list = [
"https://www.geeksforgeeks.org/what-is-ai/",
]


# content = extract_text_from_url(url)
# summary = summarize_text(content)

# print("Summary:", summary)

# "https://azure.microsoft.com/en-us/overview/what-is-cloud-computing/",
# "https://www.ibm.com/think/topics/quantum-computing",
# "https://www.techtarget.com/whatis/definition/robotics",
# "https://aws.amazon.com/what-is/quantum-computing/",
# "https://builtin.com/robotics" 



      

# # Example usage:
# # url = "https://www.mckinsey.com/featured-insights/mckinsey-explainers/what-is-blockchain"  # Replace with the actual URL
# text = extract_text_from_url_1(url)
# preprocessed_text = preprocess_text(text)
# sentences, words = tokenize_text(preprocessed_text)

# # Calculate TF-IDF and sort results
# tfidf_dict = calculate_tfidf(preprocessed_text)
# sorted_tfidf = sort_tfidf(tfidf_dict)

# # Get top N keywords
# top_keywords = get_top_keywords(sorted_tfidf, top_n=10)

# # Extract only the keywords (without scores)
# keywords_only = [keyword for keyword, score in top_keywords]

# # Output top keywords
# for keyword, score in top_keywords:
#     print(f"{keyword}: {score:.4f}")
    
# print("\nKeywords Only (Comma-Separated List):")
# print(', '.join(keywords_only))  # Comma-separated string in the output

# Insert the link and comma-separated keywords into the MongoDB database
# insert_into_database(url, keywords_only,summary)

def process_multiple_urls(urls):
    for url in urls:
        try:
            print(f"Processing: {url}")

            # Extract content and generate summary
            content = extract_text_from_url(url)
            summary = summarize_text(content)

            # Extract text and preprocess
            text = extract_text_from_url_1(url)
            preprocessed_text = preprocess_text(text)

            # Calculate TF-IDF and extract keywords
            tfidf_dict = calculate_tfidf(preprocessed_text)
            sorted_tfidf = sort_tfidf(tfidf_dict)
            top_keywords = get_top_keywords(sorted_tfidf, top_n=10)

            # Extract only the keywords (without scores)
            keywords_only = [keyword for keyword, score in top_keywords]

            # Insert URL, keywords, and summary into MongoDB
            insert_into_database(url, keywords_only, summary)

            print(f"Successfully inserted data for: {url}\n")
            print(top_keywords)

        except Exception as e:
            print(f"Error processing {url}: {e}")

process_multiple_urls(urls_list)

