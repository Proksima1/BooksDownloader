import React from 'react';
import BookItem from '../BookItem/BookItem';
import ErrorItem from '../ErrorItem/ErrorItem'
import Loader from '../Loader/Loader';


export default function BooksBlock({ books, sendJsonMessage, error, hide }) {
   const errorDoesntExist = error === undefined;
   return (
      <div className="search-results">
         <div className="search-results__wrapper">
            {(hide === true) ? (
               <Loader></Loader>
            ) : ((errorDoesntExist && books.length > 0) ? (
               books?.map((book, index) => (
                  <BookItem key={index} book={book} sendJsonMessage={sendJsonMessage} />
               ))
            ) : (
               <ErrorItem error={error} />
            ))}
         </div>
      </div>
   )
}