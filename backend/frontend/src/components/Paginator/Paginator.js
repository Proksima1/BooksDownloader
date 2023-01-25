import React, { useState, useEffect } from 'react';
import './Paginator.css';
import ReactPaginate from 'react-paginate'
import BooksBlock from '../BooksBlock/BooksBlock';
import ErrorItem from '../ErrorItem/ErrorItem';


export default function Paginator({ searchR, books, setBooks, itemsPerPage, sendJsonMessage }) {
	const [currentItems, setCurrentItems] = useState([]);
	const [pageCount, setPageCount] = useState(0);
	const [itemOffset, setItemOffset] = useState(0);

	useEffect(() => {
		if (books === 'loading') {
			setCurrentItems('');
		}
		else if (books !== '') {
			let Numbooks = books[0];
			let allbooks = books[1];
			const endOffset = itemOffset + itemsPerPage;
			console.log(`Loading items from ${itemOffset} to ${endOffset}`);
			setCurrentItems(allbooks);
			// console.log(currentItems)
			// console.log(Numbooks);
			// console.log(itemsPerPage);
			setPageCount(Math.ceil(Numbooks / itemsPerPage));
		}
	}, [itemOffset, itemsPerPage, books]);

	const handlePageClick = (event) => {
		const newOffset = event.selected * itemsPerPage % books[0];
		console.log(`User requested page number ${event.selected + 1}, which is offset ${newOffset}`);
		setItemOffset(newOffset);
		setBooks("loading");
		sendJsonMessage({ 'type': 'goToPage', 'message': [searchR, newOffset] })
	};

	return (
		<>
			{(books[0] === 0) ? (<ErrorItem error={'По данному запросу ничего не найдено'}></ErrorItem>) : ((books !== '') ? (
				<>
					<BooksBlock books={currentItems} sendJsonMessage={sendJsonMessage}></BooksBlock>
					{(books[0] <= 10) ? (<></>) :
						(<ReactPaginate
							nextLabel="следующая >"
							onPageChange={handlePageClick}
							pageRangeDisplayed={3}
							marginPagesDisplayed={2}
							pageCount={pageCount}
							previousLabel="< предыдущая"
							pageClassName="page-item"
							pageLinkClassName="page-link"
							previousClassName="page-item"
							previousLinkClassName="page-link"
							nextClassName="page-item"
							nextLinkClassName="page-link"
							breakLabel="..."
							breakClassName="page-item"
							breakLinkClassName="page-link"
							containerClassName="pagination"
							activeClassName="active"
							renderOnZeroPageCount={null}
						/>)}
				</>
			) : (
				<></>
			))}
		</>
	);
}