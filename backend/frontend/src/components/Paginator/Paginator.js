import React, { useState, useEffect } from 'react';
import './Paginator.css';
import ReactPaginate from 'react-paginate'
import BooksBlock from '../BooksBlock/BooksBlock';


const items = [...Array(33).keys()];

function Items({ currentItems }) {
   return (
      <div className="items">
         {currentItems && currentItems.map((item) => (
            <div>
               <h3>Item #{item}</h3>
            </div>
         ))}
      </div>
   );
}

export default function Paginator({ itemsPerPage, sendJsonMessage }) {
   // We start with an empty list of items.
   const [currentItems, setCurrentItems] = useState(null);
   const [pageCount, setPageCount] = useState(0);
   // Here we use item offsets; we could also use page offsets
   // following the API or data you're working with.
   const [itemOffset, setItemOffset] = useState(0);

   useEffect(() => {
      // Fetch items from another resources.
      const endOffset = itemOffset + itemsPerPage;
      console.log(`Loading items from ${itemOffset} to ${endOffset}`);
      setCurrentItems(items.slice(itemOffset, endOffset));
      setPageCount(Math.ceil(items.length / itemsPerPage));
   }, [itemOffset, itemsPerPage]);

   // Invoke when user click to request another page.
   const handlePageClick = (event) => {
      const newOffset = event.selected * itemsPerPage % items.length;
      console.log(`User requested page number ${event.selected}, which is offset ${newOffset}`);
      setItemOffset(newOffset);

      // sendJsonMessage({ 'type': 'goToPage', 'message': newOffset })
   };

   return (
      <>
         <BooksBlock hide={true}></BooksBlock>
         {/* <Items currentItems={currentItems} /> */}
         <ReactPaginate
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
         />
      </>
   );
}