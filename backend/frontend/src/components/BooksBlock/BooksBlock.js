import React from 'react';
import BookItem from '../BookItem/BookItem';
import ErrorItem from '../ErrorItem/ErrorItem'


export default function BooksBlock({ books, sendJsonMessage, error }) {
	const errorDoesntExist = error === undefined;
	return (
		<div className="search-results">
			<div className="search-results__wrapper">
				{(errorDoesntExist && books.length > 0) ? (
					books?.map((book, index) => (
						<BookItem key={index} book={book} sendJsonMessage={sendJsonMessage} />
					))
				) : (
					<ErrorItem error={error} />
				)}
			</div>
		</div>
	)
}