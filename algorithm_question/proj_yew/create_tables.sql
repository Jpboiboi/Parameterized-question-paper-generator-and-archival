-- Create table for the first set of question fragments
CREATE TABLE question_starts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    text TEXT NOT NULL
);

-- Create table for the second set of question fragments
CREATE TABLE question_ends (
    id INT PRIMARY KEY AUTO_INCREMENT,
    text TEXT NOT NULL
);

-- Insert data into question_starts
INSERT INTO question_starts (text) VALUES
('Implement insertion sort'),
('Explain O(N) time'),
('Implement palindrome check'),
('Create a binary search tree'),
('Write a function to find the maximum element'),
('Implement a linked list'),
('Create a hash table'),
('Write a function for binary search'),
('Implement quicksort'),
('Create a depth-first search algorithm'),
('Implement a breadth-first search'),
('Write a recursive factorial function'),
('Create a function to check if a number is prime'),
('Implement a stack data structure'),
('Create a queue data structure');

-- Insert data into question_ends
INSERT INTO question_ends (text) VALUES
('using arrays'),
('most efficiently'),
('using strings'),
('with a time complexity of O(log n)'),
('with a time complexity of O(n)'),
('without using built-in functions'),
('recursively'),
('iteratively'),
('using dynamic programming'),
('using a greedy approach'),
('with minimal space complexity'),
('in JavaScript'),
('in Python'),
('in Java'),
('that handles edge cases');
