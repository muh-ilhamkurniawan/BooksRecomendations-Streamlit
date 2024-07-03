import streamlit as st
import pandas as pd

# Load data
books_df = pd.read_excel('books.xlsx', header=None, names=['ID BUKU', 'JUDUL BUKU', 'PENGARANG', 'KATEGORI'])
borrowers_df = pd.read_excel('borrowers.xlsx', header=None, names=['ID PEGAWAI', 'NAMA PEGAWAI', 'JUDUL BUKU', 'PENGARANG', 'KATEGORI'])

# Replace NaN values in 'KATEGORI' column with an empty string
books_df['KATEGORI'] = books_df['KATEGORI'].fillna("")
borrowers_df['KATEGORI'] = borrowers_df['KATEGORI'].fillna("")

# Function to get books borrowed by an employee
def get_borrowed_books(employee_id):
    borrowed_books = borrowers_df[borrowers_df['ID PEGAWAI'] == int(employee_id)]
    return borrowed_books

# Knowledge-Based Filtering
def knowledge_based_recommendations(employee_id, top_n=3):
    borrowed_books = get_borrowed_books(employee_id)
    if borrowed_books.empty:
        st.write('Pegawai belum meminjam buku.')
        return pd.DataFrame()

    borrowed_books_list = borrowed_books['JUDUL BUKU'].tolist()
    borrowed_books_df = books_df[books_df['JUDUL BUKU'].isin(borrowed_books_list)]

    recommendations = []

    for _, row in books_df.iterrows():
        if row['JUDUL BUKU'] in borrowed_books_list:
            continue

        # Splitting categories by comma and removing any leading/trailing spaces
        borrowed_books_df['KATEGORI'] = borrowed_books_df['KATEGORI'].apply(lambda x: [item.strip() for item in x.split(',')])
        row_categories = [item.strip() for item in row['KATEGORI'].split(',')]

        category_score = borrowed_books_df['KATEGORI'].apply(lambda x: len(set(x) & set(row_categories)) / len(set(row_categories))).mean()
        author_score = borrowed_books_df['PENGARANG'].apply(lambda x: 1 if x == row['PENGARANG'] else 0).mean()

        total_score = 0.6 * category_score + 0.4 * author_score

        recommendations.append({
            'ID BUKU': row['ID BUKU'],
            'JUDUL BUKU': row['JUDUL BUKU'],
            'PENGARANG': row['PENGARANG'],
            'KATEGORI': row['KATEGORI'],
            'SCORE': total_score
        })

    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df = recommendations_df.sort_values(by='SCORE', ascending=False).head(top_n)
    return recommendations_df[['ID BUKU', 'JUDUL BUKU', 'PENGARANG', 'KATEGORI', 'SCORE']]

# Streamlit App
st.title('Sistem Rekomendasi Buku Berbasis Pengetahuan')

employee_id = st.text_input('Masukkan ID Pegawai:')

if st.button('Dapatkan Rekomendasi'):
    if employee_id:
        recommendations = knowledge_based_recommendations(employee_id)

        if not recommendations.empty:
            st.write(f'Rekomendasi Buku untuk ID Pegawai {employee_id} menggunakan metode Knowledge-Based:')
            st.dataframe(recommendations)
        else:
            st.write('Tidak ada rekomendasi yang ditemukan.')
    else:
        st.write('Silakan masukkan ID Pegawai.')
