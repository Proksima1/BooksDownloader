import React from 'react';

export default function ErrorItem({ error }) {
	return (
		<p className="error__text">Возникла ошибка: {error}</p>
	)
}