// SearchBar.tsx
import React, { memo, useState } from 'react';
import styled from 'styled-components/macro';
import axios from 'axios';
import { Dialog, CircularProgress } from '@mui/material';
import { csvParse, csvFormat } from 'd3-dsv';
import { csv } from 'd3';
import { writeFileSync } from 'fs';

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
    const [result, setResult] = useState<string | null>(null);

    const handleFeedback = async (rating: number) => {
      console.log(`User rating: ${rating}`);

      try {
        const allPrompts = await csv("/public/collection/prompts_db/all_prompts.csv");

        const randomIndex = Math.floor(Math.random() * allPrompts.length);
        const randomRow = allPrompts[randomIndex];

        const cols = ['A_count', 'B_count', 'C_count', 'D_count'];
        const randomCol = cols[Math.floor(Math.random() * cols.length)];

        const currentCountValue = Number(randomRow[randomCol]);
        if (currentCountValue) { // Check if count value is a number
            switch (currentCountValue) {
              case 1:
              case 2:
                randomRow[randomCol] = currentCountValue - 1;
                break;
              case 4:
              case 5:
                randomRow[randomCol] = currentCountValue + 1;
                break;
              case 3:
                break;
              default:
                console.log('No changes applied');
            }
        }

        console.log(randomRow);

        const csvContent = csvFormat(allPrompts);
        //writeFileSync('/public/collection/prompts_db/all_prompts.csv', csvContent);

        alert("Feedback recorded successfully");
      } catch (error) {
        console.error(`Error in processing feedback: ${error}`);
        alert("Failed to record feedback");
    }
    }

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
                setResult(() => "AI Agent not found, building new AI agent");   
                const response = await axios.post(
                    'http://localhost:5000/create-agent',
                    { query },
                    { headers: { 'Content-Type': 'application/json' } },
                );
                const aiResult = response.data.result;
                console.log(aiResult);
                setResult(aiResult);
                if (aiResult == "success") {
                    // If the AI agent creation was successful, then we will trigger a Search again.
                    handleSearch();
                }
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

            {/* Feedback section */}
            <div className="feedbackSection">
              <p>Rate the output:</p>
              {['⭐️', '⭐️', '⭐️', '⭐️', '⭐️'].map((star, index) => (
                <button key={index} onClick={() => handleFeedback(index + 1)}>
                  {star}
                </button>
              ))}
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

  .feedbackSection {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: row;
    gap: 1rem;

    button {
        background: none;
        border: none;
        cursor: pointer;
        color: gold;
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