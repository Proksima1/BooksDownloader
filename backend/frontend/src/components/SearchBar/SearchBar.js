import React, { useState, useCallback, useEffect, useRef } from 'react';
import useWebSocket from 'react-use-websocket';
import logo from './images/search-icon.svg'
import BooksBlock from "../BooksBlock/BooksBlock";
import Paginator from '../Paginator/Paginator';

export default function SearchBar() {
   const [countBooksOnBack, setCountBooksOnBack] = useState(false);
   const [nowRequest, setNowRequest] = useState('');
   const { sendJsonMessage, } = useWebSocket('ws://127.0.0.1:8000/ws/search', {
      onOpen: () => {
         console.log("Connected!")
      },
      onClose: () => {
         console.log("Disconnected!")

      },
      onMessage: (e) => {
         let data = JSON.parse(e.data)
         switch (data.type) {
            case 'welcome':
               console.log(data.message)
               break;
            case 'searchResponse':
               let messageSearch = data.message;
               setCountBooksOnBack(messageSearch[0]);
               messageSearch = messageSearch[1];
               if (messageSearch.length === 0) {
                  setBooks(<BooksBlock error={"По данному запросу ничего не найдено. Попробуйте использовать похожие слова или другие написания слов"} />);
               } else {
                  setBooks(<BooksBlock books={data.message} sendJsonMessage={sendMessage} />);
               }
               break;
            case 'parseResponse':
               let messageParse = data.message;
               fetch(messageParse.urlToBook, { method: 'GET' }).then(response => {
                  if (response.status !== 200) {
                     return Promise.reject();
                  }
                  return response.blob()
               }).then(blob => downloadBook(blob, messageParse.fileName))
               break;
            default:
               console.error('Такого типа нет в приеме')
               console.log(data)
               break;
         }
      },
      shouldReconnect: (closeEvent) => true,
      reconnectAttempts: 10,
      reconnectInterval: 3000,
   });

   const downloadBook = (blob, filename) => {
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
   }
   const [inputFocused, setInputFocused] = useState(false);
   const onInputFocus = () => setInputFocused(true);
   const onInputBlur = () => setInputFocused(false);
   const [isSearchedExeced, setIsSearchedExeced] = useState(false);
   const [searchBlock, setSearchBlock] = useState([]);
   const [searchInput, setSearchInput] = useState([]);
   const [books, setBooks] = useState('');
   const sendMessage = (f) => sendJsonMessage(f);

   const searchExec = useCallback((isSearchedExeced) => {
      let requestDict = { 'type': 'search', 'message': searchInput.value }
      if (searchBlock.classList.contains('searching_block')) return sendJsonMessage(requestDict);
      isSearchedExeced(true);
      setTimeout(function () {
         searchBlock.classList.add('searching_block');
         sendJsonMessage(requestDict);
      }, 1000);
   }, [sendJsonMessage, searchBlock, searchInput])

   // useEffect(() => {
   //    if () {

   //    }
   // }, [countBooksOnBack, nowRequest])

   useEffect(() => {
      const listener = event => {
         if ((event.code === "Enter" || event.code === "NumpadEnter") && inputFocused) {
            event.preventDefault();
            setNowRequest(searchInput.value);
            setBooks(<BooksBlock hide={true} />);
            searchExec(setIsSearchedExeced);
         }
      };
      document.addEventListener("keydown", listener);
      return () => {
         document.removeEventListener("keydown", listener);
      };
   }, [inputFocused, searchExec]);

   return (
      <>
         <div className="search" ref={r => setSearchBlock(r)}>
            <h1 className={!isSearchedExeced ? "search-title" : 'search-title hider'}>Найти книгу здесь</h1>
            <form className={!isSearchedExeced ? "search-form" : 'search-form search-form__up'}>
               <input onFocus={onInputFocus} onBlur={onInputBlur} type="text" placeholder="Введите название книги:" className="search-form__input" ref={ref => setSearchInput(ref)} />
               <a className="search-form__button" onClick={() => { searchExec(setIsSearchedExeced) }}>
                  <img src={logo} alt="Search icon" />
               </a>
            </form>
         </div >
         {/* <Loader></Loader> */}
         {/* {books} */}
         <Paginator itemsPerPage={10} sendJsonMessage={sendJsonMessage}></Paginator>
      </>
   )
}