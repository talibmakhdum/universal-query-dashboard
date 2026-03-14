import React from 'react'

interface QueryChipsProps {
  queries: string[]
  onClick: (query: string) => void
}

export const QueryChips: React.FC<QueryChipsProps> = ({ queries, onClick }) => {
  return (
    <div className="flex flex-wrap gap-2">
      {queries.map((query, index) => (
        <button
          key={index}
          onClick={() => onClick(query)}
          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm hover:bg-blue-200 transition-colors cursor-pointer"
        >
          {query}
        </button>
      ))}
    </div>
  )
}