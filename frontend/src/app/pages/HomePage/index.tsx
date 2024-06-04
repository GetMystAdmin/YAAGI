import * as React from 'react';
import { Helmet } from 'react-helmet-async';
import { NavBar } from 'app/components/NavBar';
import { PageWrapper } from 'app/components/PageWrapper';
import { SearchBar } from 'app/components/SearchBar'

export function HomePage() {
  return (
    <>
      <Helmet>
        <title>Home Page</title>
        <meta
          name="description"
          content="A YAAGI - Yet Another Agent of General Intelligence application homepage"
        />
      </Helmet>
      <NavBar />
      <PageWrapper>
          <SearchBar id="unique-search-bar-id" />
      </PageWrapper>
    </>
  );
}
