import React from 'react';
import BookItem from '../BookItem/BookItem';
import ErrorItem from '../ErrorItem/ErrorItem'
import Loader from '../Loader/Loader';


export default function BooksBlock({ books, sendJsonMessage, error = false, loading = false }) {
   const errorDoesntExist = error === false;
   return (
      <div className="search-results">
         <div className="search-results__wrapper">
            {(loading === true) ? (
               <Loader></Loader>
            ) : ((errorDoesntExist && books.length > 0) ? (
               books?.map((book, index) => (
                  <BookItem key={index} book={book} sendJsonMessage={sendJsonMessage} />
               ))
            ) : (
               (error == false) ? (<></>) : (<ErrorItem error={error} />)
            ))}
         </div>
      </div>
   )
}