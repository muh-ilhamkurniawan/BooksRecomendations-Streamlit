import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load data
books_df = pd.read_excel('books.xlsx', header=0)
borrowers_df = pd.read_excel('borrowers.xlsx', header=0)

# Function to get books borrowed by an employee
def get_borrowed_books(employee_id):
    borrowed_books = borrowers_df[borrowers_df['ID PEGAWAI'] == employee_id]
    return borrowed_books

# Content-Based Filtering
def content_based_recommendations(employee_id, top_n=3):
    borrowed_books = get_borrowed_books(employee_id)
    if borrowed_books.empty:
        return pd.DataFrame()

    borrowed_books_ids = borrowed_books['JUDUL BUKU'].tolist()
    borrowed_books_df = books_df[books_df['JUDUL BUKU'].isin(borrowed_books_ids)]

    # Combine category and author to create a feature for similarity
    books_df['combined_features'] = books_df['PENGARANG'] + ' ' + books_df['KATEGORI']
    borrowed_books_df['combined_features'] = borrowed_books_df['PENGARANG'] + ' ' + borrowed_books_df['KATEGORI']

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(books_df['combined_features'])

    borrowed_books_matrix = tfidf.transform(borrowed_books_df['combined_features'])
    similarity_matrix = cosine_similarity(borrowed_books_matrix, tfidf_matrix)

    similarity_scores = similarity_matrix.mean(axis=0)
    recommended_books_indices = similarity_scores.argsort()[-top_n:][::-1]
    recommended_books = books_df.iloc[recommended_books_indices]
    
    return recommended_books[['ID BUKU', 'JUDUL BUKU', 'PENGARANG', 'KATEGORI']]

# Collaborative Filtering (User-Based)
def user_based_recommendations(employee_id, top_n=3):
    borrowed_books = get_borrowed_books(employee_id)
    if borrowed_books.empty:
        return pd.DataFrame()

    employee_books = borrowed_books['JUDUL BUKU'].tolist()
    employee_borrowed = borrowers_df[borrowers_df['JUDUL BUKU'].isin(employee_books)]

    user_book_matrix = pd.pivot_table(employee_borrowed, values='JUDUL BUKU', index='ID PEGAWAI', columns='JUDUL BUKU', aggfunc='count', fill_value=0)
    similarity_matrix = cosine_similarity(user_book_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_book_matrix.index, columns=user_book_matrix.index)
    
    similar_users = similarity_df[employee_id].sort_values(ascending=False).index[1:top_n+1]
    similar_users_books = borrowers_df[borrowers_df['ID PEGAWAI'].isin(similar_users)]
    
    recommended_books = similar_users_books[~similar_users_books['JUDUL BUKU'].isin(employee_books)]
    top_recommended_books = recommended_books['JUDUL BUKU'].value_counts().index[:top_n]
    recommended_books_df = books_df[books_df['JUDUL BUKU'].isin(top_recommended_books)]
    
    return recommended_books_df[['ID BUKU', 'JUDUL BUKU', 'PENGARANG', 'KATEGORI']]

# Collaborative Filtering (Item-Based)
def item_based_recommendations(employee_id, top_n=3):
    borrowed_books = get_borrowed_books(employee_id)
    if borrowed_books.empty:
        return pd.DataFrame()

    employee_books = borrowed_books['JUDUL BUKU'].tolist()
    employee_borrowed = borrowers_df[borrowers_df['JUDUL BUKU'].isin(employee_books)]

    book_user_matrix = pd.pivot_table(employee_borrowed, values='JUDUL BUKU', index='JUDUL BUKU', columns='ID PEGAWAI', aggfunc='count', fill_value=0)
    similarity_matrix = cosine_similarity(book_user_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=book_user_matrix.index, columns=book_user_matrix.index)
    
    similar_books = pd.Series()
    for book in employee_books:
        similar_books = similar_books.append(similarity_df[book].sort_values(ascending=False).iloc[1:top_n+1])
    
    recommended_books = similar_books.index.difference(employee_books)
    recommended_books_df = books_df[books_df['JUDUL BUKU'].isin(recommended_books[:top_n])]
    
    return recommended_books_df[['ID BUKU', 'JUDUL BUKU', 'PENGARANG', 'KATEGORI']]

# Streamlit App
st.title('Sistem Rekomendasi Buku')

employee_id = st.text_input('Masukkan ID Pegawai:')
method = st.selectbox('Pilih Metode Rekomendasi:', ['Content-Based', 'User-Based Collaborative', 'Item-Based Collaborative'])

if st.button('Dapatkan Rekomendasi'):
    if employee_id:
        if method == 'Content-Based':
            recommendations = content_based_recommendations(employee_id)
        elif method == 'User-Based Collaborative':
            recommendations = user_based_recommendations(employee_id)
        else:
            recommendations = item_based_recommendations(employee_id)
        
        if not recommendations.empty:
            st.write(f'Rekomendasi Buku untuk ID Pegawai {employee_id} menggunakan metode {method}:')
            st.dataframe(recommendations)
        else:
            st.write('Tidak ada rekomendasi yang ditemukan.')
    else:
        st.write('Silakan masukkan ID Pegawai.')
