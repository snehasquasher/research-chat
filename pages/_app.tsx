// pages/_app.tsx
import React, { useState } from 'react';
import '../globals.css';
import RootLayout from '../components/RootLayout';

function MyApp({ Component, pageProps }: { Component: React.ComponentType; pageProps: any }) {



	return (
		<RootLayout>
			<Component {...pageProps} />
		</RootLayout>
	);
}

export default MyApp;
