import React, { useState, useEffect } from 'react';
import logo from './images/download-icon.svg'

export default function BookItem({ book, sendJsonMessage }) {
	const [url, setUrl] = useState(book.downloadUrl);
	const parseBook = (e) => {
		e.stopPropagation();
		sendJsonMessage({ 'type': 'parse', 'message': url })
	}

	useEffect(() => {
		if (book.downloadUrl !== url) {
			setUrl(book.downloadUrl);
		}
	}, [book.downloadUrl, url]);

	return (
		<div className="book-item">
			<div className="book-item__about">
				<img src={book?.cover} alt="Book cover" className="book-item__cover" />
				<div className="book-item__desc-block">
					<h1 className="book-item__title">{book?.title}</h1>
					<p className="book-item__author">{book?.author}</p>
					<i className="book-item__source">Источник: <a rel="noopener" target="_blank" href={book?.downloadUrl}>{book?.source}</a></i>
				</div>
			</div>
			<a data-url={book.downloadUrl} onClick={(e) => parseBook(e)} className="book-item__download">
				<img src={logo} alt="Download icon" />
			</a>
		</div >
	)
}