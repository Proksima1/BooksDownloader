import React from 'react';
import BookItem from '../BookItem/BookItem';


export default function BooksBlock({ books, sendJsonMessage }) {
	return (
		<div className="search-results">
			<div className="search-results__wrapper">
				{(books.length > 0) ? (
					books?.map((book, index) => (
						<BookItem key={index} book={book} sendJsonMessage={sendJsonMessage} />
					))
				) : (
					<></>
				)}
			</div>
		</div>
	)
}