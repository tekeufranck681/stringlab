export interface AlgorithmConfig {
  id: string;
  title: string;
  description: string;
  category: string;
  endpoint: string;

  complexity: {
    time: string;
    space: string;
  };

  inputs: {
    name: string;
    label: string;
    type: string;
  }[];
}

export const algorithms: AlgorithmConfig[] = [
  {
    id: "palindrome",

    title: "Palindrome Detection",

    description:
      "Determine whether a string reads the same forwards and backwards.",

    category: "Analysis & Properties",

    endpoint: "/analysis/palindrome",

    complexity: {
      time: "O(n)",
      space: "O(1)",
    },

    inputs: [
      {
        name: "text",
        label: "Input String",
        type: "text",
      },
    ],
  },

  {
    id: "frequency",

    title: "Character Frequency Analysis",

    description: "Count occurrences of every character.",

    category: "Analysis & Properties",

    endpoint: "/analysis/frequency",

    complexity: {
      time: "O(n)",
      space: "O(k)",
    },

    inputs: [
      {
        name: "text",
        label: "Input String",
        type: "text",
      },
    ],
  },

  {
    id: "longest-palindrome",

    title: "Longest Palindromic Substring",

    description: "Find the longest palindrome inside a string.",

    category: "Analysis & Properties",

    endpoint: "/analysis/longest-palindrome",

    complexity: {
      time: "O(n²)",
      space: "O(1)",
    },

    inputs: [
      {
        name: "text",
        label: "Input String",
        type: "text",
      },
    ],
  },
];
