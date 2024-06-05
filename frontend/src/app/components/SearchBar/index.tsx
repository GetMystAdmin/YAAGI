// SearchBar.tsx
import React, { memo, useState } from 'react';
import styled from 'styled-components/macro';
import axios from 'axios';
import { Dialog, CircularProgress } from '@mui/material';

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
    const [isLoading, setLoading] = useState(false);
    const [query, setQuery] = useState('');
    const [result, setResult] = useState<string|null>(null);

    // Trigger the API call when button is pressed
    const handleSearch = async () => {
        setLoading(true);
        try {
            const response = await axios.post(
                'http://localhost:5000/search',
                { query },
                { headers: { 'Content-Type': 'application/json' } },
            );
            const { filename } = response.data;
            setResult(filename);
            console.log(filename);
            
            if(filename){
                const aiResponse = await axios.post(
                    'http://localhost:5000/ask-ai',
                    { filename, query },
                    { headers: { 'Content-Type': 'application/json' } },
                );
                const aiResult = aiResponse.data.file_output;
                // You can process aiResult here as needed.
                setResult(aiResult);
                console.log(aiResult);
            }
            else {
                // Displaying a default message when AI Agent is not found.
                setResult(() => "AI Agent not found, building new AI agent");   
            }

        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Wrapper className={className}>
            <div className="inputSection">
                <input
                    type="text"
                    id={id}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    {...restOf}
                />
                <button onClick={handleSearch}>→</button>
            </div>

            <Dialog open={isLoading} PaperProps={{
                    style: {
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                        boxShadow: 'none',
                        overflow: 'hidden',
                    }
                }}>
                <CircularLoading/>
            </Dialog>

            <div className="resultSection">
                {result && <pre>{result}</pre>}
            </div>
        </Wrapper>
    );
  },
);

const Wrapper = styled.div`
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  flex-direction: column;

  .inputSection {
    display: flex;
    justify-content: center;
    align-items: center;
    input[type='text'] {
        margin-right: 5px;
        padding: 5px;
        width: 100%;
    }

    button {
        background-color: green;
        color: white;
        border: none;
        padding: 5px 10px;
    }
  }

    .resultSection {
        display: flex;
        justify-content: center;
        align-items: center;
        color: #ffffff;
        width: 80%;   /* Set the square size */
        height: 40%;  /* Set the square size */
        border: 1px solid gray; /* Add a border */
        overflow-y: scroll;  /* Set vertical overflow to scroll */
        word-wrap: break-word; /* Make the word wrap */
    }
`;

const CircularLoading = styled.div`
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ffffff;

  > div {
    <CircularProgress />
  }
`;