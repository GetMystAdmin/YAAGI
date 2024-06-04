// SearchBar.tsx
import React, { memo } from 'react';
import styled from 'styled-components/macro';

type InputProps = React.DetailedHTMLProps<
  React.InputHTMLAttributes<HTMLInputElement>,
  HTMLInputElement
>;

interface Props extends InputProps {
  id: string;
  className?: string;
}

export const SearchBar = memo(
  ({ id, className, ...restOf }: Props) => {
    return (
      <Wrapper className={className}>
        <input type="text" id={id} {...restOf} />
        <button onClick={() => alert('Button clicked')}>→</button>
      </Wrapper>
    );
  },
);

const Wrapper = styled.div`
  // Added styles to center the div in middle of the page.
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;

  input[type='text'] {
    margin-right: 5px;
    padding: 5px;
    width: 60%;
  }

  button {
    background-color: green;
    color: white;
    border: none;
    padding: 5px 10px;
  }
`;
