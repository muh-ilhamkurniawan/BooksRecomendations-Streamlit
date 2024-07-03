import streamlit as st
import pandas as pd
from collections import Counter

# Load data from Excel file
@st.cache_data  # Cache data to improve performance
def load_data(file_path):
    df = pd.read_excel(file_path)
    # Split values in 'KATEGORI' column if separated by comma and expand into multiple rows
    df = df.assign(KATEGORI=df['KATEGORI'].str.split(',')).explode('KATEGORI').reset_index(drop=True)
    return df

# Function to recommend books with weights
def recommend_books(df, authors, categories, author_weight=0.4, category_weight=0.6):
    # Create a column 'WEIGHT' with default value 0
    df = df.copy()  # Clone DataFrame to avoid mutating cached object
    df['WEIGHT'] = 0
    
    # Count occurrences of categories for each employee
    category_counts = df.groupby(['ID PEGAWAI', 'KATEGORI']).size().reset_index(name='COUNT')
    
    # Filter by authors and categories
    if authors:
        df.loc[df['PENGARANG'].isin(authors), 'WEIGHT'] += author_weight
    if categories:
        for category in categories:
            if category in category_counts['KATEGORI'].values:
                df.loc[df['KATEGORI'] == category, 'WEIGHT'] += category_weight * category_counts.loc[category_counts['KATEGORI'] == category, 'COUNT'].values[0]
    
    # Sort by WEIGHT descending
    recommended_books = df.sort_values(by='WEIGHT', ascending=False)[['JUDUL BUKU', 'WEIGHT']]
    return recommended_books

# Main Streamlit program
def main():
    st.title('Sistem Rekomendasi Buku')
    st.sidebar.title('Pilih Kriteria')

    # Load data buku
    file_path = 'books.xlsx'
    df = load_data(file_path)

    # Sidebar for selecting authors and categories
    authors = st.sidebar.multiselect('Pilih Pengarang', df['PENGARANG'].unique())
    categories = st.sidebar.multiselect('Pilih Kategori', df['KATEGORI'].unique())

    # Button to recommend books based on selected authors and categories
    if st.sidebar.button('Rekomendasikan'):
        recommended_books = recommend_books(df, authors, categories)
        st.success('Berikut ini adalah daftar buku beserta nilai rekomendasinya:')
        st.write(recommended_books)

    # Load data peminjaman buku oleh pegawai
    file_path_employe = 'borrowers.xlsx'
    df_employe = load_data(file_path_employe)

    # Sidebar for selecting employee and fetching their borrowed authors and categories
    selected_employee = st.sidebar.selectbox('Pilih Pegawai', df_employe['NAMA PEGAWAI'].unique())
    categories_employe = df_employe[df_employe['NAMA PEGAWAI'] == selected_employee]['KATEGORI'].str.split(',').explode().str.strip().tolist()

    # Button to recommend books based on selected employee's borrowed authors and categories
    if st.sidebar.button('Rekomendasikan Per User'):
        recommended_books = recommend_books(df_employe, [], categories_employe)  # No authors filtering
        st.success(f'Buku-buku yang direkomendasikan untuk {selected_employee}:')
        st.write(recommended_books)

# Call main function to run the application
if __name__ == '__main__':
    main()
