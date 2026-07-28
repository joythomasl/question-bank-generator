"""
fix_all_solutions_part2.py — Codeforces (classic replacements), CSES, HackerRank, GeeksforGeeks
This file is imported by fix_all_solutions.py
"""

PROBLEMS_PART2 = {}

# ---------------------------------------------------------------------------
# CODEFORCES — 13 CLASSIC WELL-KNOWN PROBLEMS (replacing advanced contest ones)
# ---------------------------------------------------------------------------

PROBLEMS_PART2["codeforces:4A"] = {
    "title": "Watermelon",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/4/A",
    "source_id": "4A",
    "category": "Math",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Pete and Billy have a watermelon that weighs w kilos. They want to divide it into two parts, each weighing an even number of kilos. Determine if this is possible.",
    "examples": [
        {"input": "w = 8", "output": "true", "explanation": "8 can be split into 2+6 or 4+4."},
        {"input": "w = 3", "output": "false", "explanation": "3 cannot be split into two even parts."},
        {"input": "w = 2", "output": "false", "explanation": "2 can only be split into 1+1, both odd."}
    ],
    "constraints": ["1 <= w <= 100"],
    "solution_python": (
        "def solve(w):\n"
        "    return w > 2 and w % 2 == 0\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static boolean solve(int w) {\n"
        "        return w > 2 && w % 2 == 0;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"w": 8}, {"w": 3}, {"w": 2}, {"w": 1}, {"w": 4},
        {"w": 5}, {"w": 6}, {"w": 100}, {"w": 99}, {"w": 10},
    ]
}

PROBLEMS_PART2["codeforces:1A"] = {
    "title": "Theatre Square",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/1/A",
    "source_id": "1A",
    "category": "Math",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Theatre Square in the capital city has dimensions n x m meters. It needs to be paved with square granite flagstones of size a x a. Each flagstone costs one unit. What is the minimum number of flagstones needed? It is allowed to cover a larger area than the Theatre Square, but the Square must be covered. It is not allowed to break the flagstones.",
    "examples": [
        {"input": "n = 6, m = 6, a = 4", "output": "4", "explanation": "ceil(6/4) * ceil(6/4) = 2 * 2 = 4"}
    ],
    "constraints": ["1 <= n, m, a <= 10^9"],
    "solution_python": (
        "def solve(n, m, a):\n"
        "    import math\n"
        "    return math.ceil(n / a) * math.ceil(m / a)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static long solve(long n, long m, long a) {\n"
        "        return ((n + a - 1) / a) * ((m + a - 1) / a);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 6, "m": 6, "a": 4}, {"n": 1, "m": 1, "a": 1}, {"n": 2, "m": 1, "a": 1},
        {"n": 2, "m": 3, "a": 4}, {"n": 1000000000, "m": 1000000000, "a": 1},
        {"n": 100, "m": 100, "a": 3}, {"n": 12, "m": 13, "a": 4},
        {"n": 1, "m": 1000000000, "a": 999999999}, {"n": 7, "m": 7, "a": 7},
        {"n": 10, "m": 10, "a": 3},
    ]
}

PROBLEMS_PART2["codeforces:71A"] = {
    "title": "Way Too Long Words",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/71/A",
    "source_id": "71A",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Sometimes some words are too long. If a word has more than 10 characters, abbreviate it by replacing the middle characters with the count of characters between first and last character.",
    "examples": [
        {"input": "word = \"localization\"", "output": "\"l10n\"", "explanation": "12 > 10, so abbreviate: l + 10 + n"},
        {"input": "word = \"cat\"", "output": "\"cat\"", "explanation": "3 <= 10, no abbreviation needed"}
    ],
    "constraints": ["1 <= len(word) <= 100", "word consists of lowercase English letters"],
    "solution_python": (
        "def solve(word):\n"
        "    if len(word) <= 10:\n"
        "        return word\n"
        "    return word[0] + str(len(word) - 2) + word[-1]\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(String word) {\n"
        "        if (word.length() <= 10) return word;\n"
        "        return \"\" + word.charAt(0) + (word.length() - 2) + word.charAt(word.length() - 1);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"word": "localization"}, {"word": "cat"}, {"word": "abcdefghijk"},
        {"word": "internationalization"}, {"word": "pneumonoultramicroscopicsilicovolcanoconiosis"},
        {"word": "abcdefghij"}, {"word": "a"}, {"word": "ab"},
        {"word": "competition"}, {"word": "codeforces"},
    ]
}

PROBLEMS_PART2["codeforces:231A"] = {
    "title": "Team",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/231/A",
    "source_id": "231A",
    "category": "Implementation",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Three friends participate in a programming contest. Each problem has three binary values indicating if each friend is sure about the solution. They will implement a solution only if at least two of three are sure. How many problems will they implement?",
    "examples": [
        {"input": "problems = [[1,1,0],[1,1,1],[1,0,0],[0,1,1]]", "output": "3", "explanation": "Problems 1, 2, and 4 have at least 2 sure friends."}
    ],
    "constraints": ["1 <= n <= 1000"],
    "solution_python": (
        "def solve(problems):\n"
        "    return sum(1 for p in problems if sum(p) >= 2)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[][] problems) {\n"
        "        int count = 0;\n"
        "        for (int[] p : problems) {\n"
        "            int sum = 0;\n"
        "            for (int v : p) sum += v;\n"
        "            if (sum >= 2) count++;\n"
        "        }\n"
        "        return count;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"problems": [[1,1,0],[1,1,1],[1,0,0],[0,1,1]]},
        {"problems": [[1,0,0],[0,1,0],[0,0,1]]},
        {"problems": [[1,1,1]]},
        {"problems": [[0,0,0]]},
        {"problems": [[1,1,1],[1,1,1],[1,1,1]]},
        {"problems": [[0,0,0],[0,0,0]]},
        {"problems": [[1,0,1],[0,1,1],[1,1,0]]},
        {"problems": [[1,0,0],[0,0,0],[0,0,1],[1,1,0]]},
        {"problems": [[1,1,0]]},
        {"problems": [[0,1,1],[1,0,1]]},
    ]
}

PROBLEMS_PART2["codeforces:158A"] = {
    "title": "Next Round",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/158/A",
    "source_id": "158A",
    "category": "Implementation",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Given scores of n participants sorted in non-increasing order and a threshold position k, count how many participants advance to the next round. A participant advances if their score is positive and >= the score of the participant at position k.",
    "examples": [
        {"input": "scores = [5,4,3,2,1], k = 3", "output": "3", "explanation": "Threshold score is 3. Scores 5, 4, 3 pass."},
        {"input": "scores = [5,5,5,5,5], k = 3", "output": "5", "explanation": "All scores equal the threshold and are positive."}
    ],
    "constraints": ["1 <= k <= n <= 50", "0 <= score_i <= 100"],
    "solution_python": (
        "def solve(scores, k):\n"
        "    threshold = scores[k - 1]\n"
        "    if threshold <= 0:\n"
        "        return sum(1 for s in scores if s > 0)\n"
        "    return sum(1 for s in scores if s >= threshold)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] scores, int k) {\n"
        "        int threshold = scores[k - 1];\n"
        "        int count = 0;\n"
        "        for (int s : scores) {\n"
        "            if (threshold <= 0) {\n"
        "                if (s > 0) count++;\n"
        "            } else {\n"
        "                if (s >= threshold) count++;\n"
        "            }\n"
        "        }\n"
        "        return count;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"scores": [5, 4, 3, 2, 1], "k": 3},
        {"scores": [5, 5, 5, 5, 5], "k": 3},
        {"scores": [10, 9, 8, 7, 6, 5], "k": 4},
        {"scores": [0, 0, 0], "k": 2},
        {"scores": [100], "k": 1},
        {"scores": [1, 1, 1, 1], "k": 2},
        {"scores": [3, 2, 1, 0, 0], "k": 3},
        {"scores": [10, 10, 10, 5, 5], "k": 2},
        {"scores": [5, 0], "k": 2},
        {"scores": [7, 7, 7, 7], "k": 4},
    ]
}

PROBLEMS_PART2["codeforces:236A"] = {
    "title": "Boy or Girl",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/236/A",
    "source_id": "236A",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Given a username (a string of lowercase letters), determine if the number of distinct characters is even or odd. If even, print 'CHAT WITH HER!'. If odd, print 'IGNORE HIM!'.",
    "examples": [
        {"input": "username = \"wjmzbmr\"", "output": "\"CHAT WITH HER!\"", "explanation": "6 distinct chars (w,j,m,z,b,r) — even."},
        {"input": "username = \"xiaodao\"", "output": "\"IGNORE HIM!\"", "explanation": "5 distinct chars (x,i,a,o,d) — odd."}
    ],
    "constraints": ["1 <= len(username) <= 100", "username consists of lowercase English letters"],
    "solution_python": (
        "def solve(username):\n"
        "    distinct = len(set(username))\n"
        "    return 'CHAT WITH HER!' if distinct % 2 == 0 else 'IGNORE HIM!'\n"
    ),
    "solution_java": (
        "import java.util.*;\n"
        "public class Solution {\n"
        "    public static String solve(String username) {\n"
        "        Set<Character> set = new HashSet<>();\n"
        "        for (char c : username.toCharArray()) set.add(c);\n"
        "        return set.size() % 2 == 0 ? \"CHAT WITH HER!\" : \"IGNORE HIM!\";\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"username": "wjmzbmr"}, {"username": "xiaodao"}, {"username": "a"},
        {"username": "ab"}, {"username": "abc"}, {"username": "aabb"},
        {"username": "aaaa"}, {"username": "abcdef"},
        {"username": "zzzzz"}, {"username": "abcde"},
    ]
}

PROBLEMS_PART2["codeforces:282A"] = {
    "title": "Bit++",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/282/A",
    "source_id": "282A",
    "category": "Implementation",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "You are given n statements in Bit++ language. Each statement is either '++X', 'X++' (increment X by 1), '--X', or 'X--' (decrement X by 1). X starts at 0. Return the final value of X.",
    "examples": [
        {"input": "statements = [\"++X\", \"X++\", \"--X\"]", "output": "1", "explanation": "0 + 1 + 1 - 1 = 1"}
    ],
    "constraints": ["1 <= n <= 150"],
    "solution_python": (
        "def solve(statements):\n"
        "    x = 0\n"
        "    for s in statements:\n"
        "        if '++' in s:\n"
        "            x += 1\n"
        "        else:\n"
        "            x -= 1\n"
        "    return x\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(String[] statements) {\n"
        "        int x = 0;\n"
        "        for (String s : statements) {\n"
        "            if (s.contains(\"++\")) x++;\n"
        "            else x--;\n"
        "        }\n"
        "        return x;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"statements": ["++X", "X++", "--X"]},
        {"statements": ["X++"]},
        {"statements": ["--X"]},
        {"statements": ["X++", "X++", "X++"]},
        {"statements": ["--X", "--X", "--X"]},
        {"statements": ["++X", "--X"]},
        {"statements": ["X++", "X--", "++X", "--X"]},
        {"statements": ["++X", "++X", "++X", "++X", "++X"]},
        {"statements": ["X--", "X--"]},
        {"statements": ["++X", "X++", "++X", "X++", "--X"]},
    ]
}

PROBLEMS_PART2["codeforces:263A"] = {
    "title": "Beautiful Matrix",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/263/A",
    "source_id": "263A",
    "category": "Implementation",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "You have a 5x5 matrix with exactly one '1' and the rest '0's. In one move, you can swap any two adjacent cells. Find the minimum number of moves to move the '1' to the center of the matrix (position [2][2], 0-indexed).",
    "examples": [
        {"input": "matrix = [[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]", "output": "3", "explanation": "The 1 is at (1,4). Moves needed: |1-2| + |4-2| = 3."}
    ],
    "constraints": ["Matrix is always 5x5", "Exactly one cell is 1, rest are 0"],
    "solution_python": (
        "def solve(matrix):\n"
        "    for i in range(5):\n"
        "        for j in range(5):\n"
        "            if matrix[i][j] == 1:\n"
        "                return abs(i - 2) + abs(j - 2)\n"
        "    return 0\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[][] matrix) {\n"
        "        for (int i = 0; i < 5; i++) {\n"
        "            for (int j = 0; j < 5; j++) {\n"
        "                if (matrix[i][j] == 1) {\n"
        "                    return Math.abs(i - 2) + Math.abs(j - 2);\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "        return 0;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"matrix": [[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]},
        {"matrix": [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]]},
        {"matrix": [[1,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]},
        {"matrix": [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,1]]},
        {"matrix": [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,0]]},
        {"matrix": [[0,0,0,0,0],[0,1,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]},
        {"matrix": [[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]},
        {"matrix": [[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]},
        {"matrix": [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0]]},
        {"matrix": [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]]},
    ]
}

PROBLEMS_PART2["codeforces:339A"] = {
    "title": "Helpful Maths",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/339/A",
    "source_id": "339A",
    "category": "Sorting",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "You are given a mathematical expression in the form of a sum of 1s, 2s, and 3s (e.g., '3+2+1'). Rearrange the summands in non-decreasing order and return the result.",
    "examples": [
        {"input": "expr = \"3+2+1\"", "output": "\"1+2+3\"", "explanation": "Sort the numbers: 1, 2, 3"},
        {"input": "expr = \"1+1+3+1+3\"", "output": "\"1+1+1+3+3\"", "explanation": "Sort the numbers: 1, 1, 1, 3, 3"}
    ],
    "constraints": ["Expression contains only +, 1, 2, 3", "1 <= number of summands <= 100"],
    "solution_python": (
        "def solve(expr):\n"
        "    nums = sorted(expr.split('+'))\n"
        "    return '+'.join(nums)\n"
    ),
    "solution_java": (
        "import java.util.*;\n"
        "public class Solution {\n"
        "    public static String solve(String expr) {\n"
        "        String[] parts = expr.split(\"\\\\+\");\n"
        "        Arrays.sort(parts);\n"
        "        return String.join(\"+\", parts);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"expr": "3+2+1"}, {"expr": "1+1+3+1+3"}, {"expr": "1"},
        {"expr": "2+1"}, {"expr": "3+3+3"}, {"expr": "1+2+3+1+2+3"},
        {"expr": "3+1"}, {"expr": "2+2+2+2"}, {"expr": "1+1+1+1+1"},
        {"expr": "3+2+1+2+3+1"},
    ]
}

PROBLEMS_PART2["codeforces:96A"] = {
    "title": "Football",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/96/A",
    "source_id": "96A",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Given a string of 0s and 1s representing players in a line, determine if there are 7 or more consecutive identical characters. If yes, return 'YES', otherwise 'NO'.",
    "examples": [
        {"input": "line = \"001001\"", "output": "\"NO\"", "explanation": "No 7 consecutive identical characters."},
        {"input": "line = \"1000000001\"", "output": "\"YES\"", "explanation": "There are 8 consecutive 0s."}
    ],
    "constraints": ["1 <= len(line) <= 100", "line consists of '0' and '1'"],
    "solution_python": (
        "def solve(line):\n"
        "    return 'YES' if '0000000' in line or '1111111' in line else 'NO'\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(String line) {\n"
        "        return (line.contains(\"0000000\") || line.contains(\"1111111\")) ? \"YES\" : \"NO\";\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"line": "001001"}, {"line": "1000000001"}, {"line": "1111111"},
        {"line": "0000000"}, {"line": "00100110"}, {"line": "1111111111"},
        {"line": "10101010101010"}, {"line": "00000001111111"},
        {"line": "0"}, {"line": "1100110011001100"},
    ]
}

PROBLEMS_PART2["codeforces:112A"] = {
    "title": "Petya and Strings",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/112/A",
    "source_id": "112A",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Given two strings of equal length (lowercase and uppercase letters), compare them case-insensitively. Return -1 if the first is less, 0 if equal, 1 if the first is greater.",
    "examples": [
        {"input": "s1 = \"aaaa\", s2 = \"aaaA\"", "output": "0", "explanation": "Same when case-insensitive."},
        {"input": "s1 = \"abs\", s2 = \"Abz\"", "output": "-1", "explanation": "'abs' < 'abz' lexicographically."}
    ],
    "constraints": ["1 <= len(s) <= 100"],
    "solution_python": (
        "def solve(s1, s2):\n"
        "    a, b = s1.lower(), s2.lower()\n"
        "    if a < b: return -1\n"
        "    if a > b: return 1\n"
        "    return 0\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(String s1, String s2) {\n"
        "        int cmp = s1.toLowerCase().compareTo(s2.toLowerCase());\n"
        "        if (cmp < 0) return -1;\n"
        "        if (cmp > 0) return 1;\n"
        "        return 0;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"s1": "aaaa", "s2": "aaaA"}, {"s1": "abs", "s2": "Abz"},
        {"s1": "a", "s2": "b"}, {"s1": "b", "s2": "a"},
        {"s1": "Hello", "s2": "hello"}, {"s1": "abc", "s2": "abd"},
        {"s1": "z", "s2": "a"}, {"s1": "ABC", "s2": "abc"},
        {"s1": "aaa", "s2": "aab"}, {"s1": "xyz", "s2": "XYZ"},
    ]
}

PROBLEMS_PART2["codeforces:50A"] = {
    "title": "Domino Paving",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/50/A",
    "source_id": "50A",
    "category": "Math",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "Given an M x N board, find the maximum number of 2x1 dominoes that can be placed on it. Each domino covers exactly two cells. No two dominoes overlap.",
    "examples": [
        {"input": "m = 2, n = 3", "output": "3", "explanation": "2*3 = 6 cells, 6/2 = 3 dominoes"},
        {"input": "m = 2, n = 4", "output": "4", "explanation": "2*4 = 8 cells, 8/2 = 4 dominoes"}
    ],
    "constraints": ["1 <= m, n <= 16"],
    "solution_python": (
        "def solve(m, n):\n"
        "    return (m * n) // 2\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int m, int n) {\n"
        "        return (m * n) / 2;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"m": 2, "n": 3}, {"m": 2, "n": 4}, {"m": 1, "n": 1},
        {"m": 1, "n": 2}, {"m": 3, "n": 3}, {"m": 4, "n": 4},
        {"m": 5, "n": 5}, {"m": 16, "n": 16}, {"m": 1, "n": 10},
        {"m": 3, "n": 4},
    ]
}

PROBLEMS_PART2["codeforces:546A"] = {
    "title": "Soldier and Bananas",
    "source_site": "codeforces",
    "source_url": "https://codeforces.com/problemset/problem/546/A",
    "source_id": "546A",
    "category": "Math",
    "difficulty": "Easy",
    "companies": ["Codeforces"],
    "problem_statement": "A soldier wants to buy w bananas from a shop where the i-th banana costs i*k dollars. He has n dollars. How many more dollars does he need? If he already has enough, the answer is 0.",
    "examples": [
        {"input": "k = 3, n = 17, w = 4", "output": "13", "explanation": "Total cost = 3*(1+2+3+4) = 30. He has 17, needs 13 more."},
        {"input": "k = 1, n = 2, w = 1", "output": "0", "explanation": "Total cost = 1. He has 2, needs 0 more."}
    ],
    "constraints": ["1 <= k, w <= 1000", "0 <= n <= 10^9"],
    "solution_python": (
        "def solve(k, n, w):\n"
        "    total = k * w * (w + 1) // 2\n"
        "    return max(0, total - n)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static long solve(int k, long n, int w) {\n"
        "        long total = (long) k * w * (w + 1) / 2;\n"
        "        return Math.max(0, total - n);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"k": 3, "n": 17, "w": 4}, {"k": 1, "n": 2, "w": 1},
        {"k": 1, "n": 0, "w": 1}, {"k": 10, "n": 0, "w": 10},
        {"k": 1, "n": 100, "w": 10}, {"k": 5, "n": 100, "w": 5},
        {"k": 1000, "n": 1000000000, "w": 1000}, {"k": 1, "n": 1, "w": 1},
        {"k": 2, "n": 10, "w": 3}, {"k": 100, "n": 0, "w": 2},
    ]
}


# ---------------------------------------------------------------------------
# CSES (12 problems — 3 already done in part1 via leetcode patterns, doing all 12 CSES)
# ---------------------------------------------------------------------------

PROBLEMS_PART2["cses:1068"] = {
    "title": "Weird Algorithm",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1068",
    "source_id": "1068",
    "category": "Simulation",
    "difficulty": "Easy",
    "companies": ["Google", "CSES"],
    "problem_statement": "Consider an algorithm that takes as input a positive integer n. If n is even, divide it by two. If n is odd, multiply it by three and add one. Repeat until n is 1. Print all values of n during the process.",
    "examples": [
        {"input": "n = 3", "output": "\"3 10 5 16 8 4 2 1\"", "explanation": "3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1"}
    ],
    "constraints": ["1 <= n <= 10^6"],
    "solution_python": (
        "def solve(n):\n"
        "    res = [n]\n"
        "    while n > 1:\n"
        "        if n % 2 == 0: n //= 2\n"
        "        else: n = 3 * n + 1\n"
        "        res.append(n)\n"
        "    return ' '.join(map(str, res))\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(int n) {\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        long curr = n;\n"
        "        sb.append(curr);\n"
        "        while (curr > 1) {\n"
        "            if (curr % 2 == 0) curr /= 2;\n"
        "            else curr = 3 * curr + 1;\n"
        "            sb.append(\" \").append(curr);\n"
        "        }\n"
        "        return sb.toString();\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 3}, {"n": 1}, {"n": 2}, {"n": 4}, {"n": 5},
        {"n": 6}, {"n": 7}, {"n": 8}, {"n": 9}, {"n": 10},
    ]
}

PROBLEMS_PART2["cses:1083"] = {
    "title": "Missing Number",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1083",
    "source_id": "1083",
    "category": "Mathematics",
    "difficulty": "Easy",
    "companies": ["Amazon", "Google", "CSES"],
    "problem_statement": "You are given all numbers between 1, 2, ..., n except one. Your task is to find the missing number.",
    "examples": [
        {"input": "n = 5, nums = [2,3,1,5]", "output": "4", "explanation": "4 is missing from 1..5"}
    ],
    "constraints": ["2 <= n <= 2*10^5"],
    "solution_python": (
        "def solve(n, nums):\n"
        "    total = n * (n + 1) // 2\n"
        "    return total - sum(nums)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int n, int[] nums) {\n"
        "        long total = (long) n * (n + 1) / 2;\n"
        "        long sum = 0;\n"
        "        for (int x : nums) sum += x;\n"
        "        return (int)(total - sum);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 5, "nums": [2, 3, 1, 5]},
        {"n": 2, "nums": [1]}, {"n": 2, "nums": [2]},
        {"n": 3, "nums": [1, 3]}, {"n": 4, "nums": [1, 2, 4]},
        {"n": 5, "nums": [1, 2, 3, 4]}, {"n": 6, "nums": [6, 5, 4, 3, 1]},
        {"n": 7, "nums": [1, 2, 3, 4, 5, 6]}, {"n": 8, "nums": [8, 7, 6, 5, 4, 3, 2]},
        {"n": 10, "nums": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    ]
}

PROBLEMS_PART2["cses:1069"] = {
    "title": "Repetitions",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1069",
    "source_id": "1069",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "Given a DNA sequence (a string of characters A, C, G, T), find the length of the longest repetition (consecutive identical characters).",
    "examples": [
        {"input": "dna = \"ATTCGGGA\"", "output": "3", "explanation": "The longest repetition is 'GGG' with length 3."}
    ],
    "constraints": ["1 <= len(dna) <= 10^6", "dna consists of characters A, C, G, T"],
    "solution_python": (
        "def solve(dna):\n"
        "    if not dna:\n"
        "        return 0\n"
        "    max_len = 1\n"
        "    cur_len = 1\n"
        "    for i in range(1, len(dna)):\n"
        "        if dna[i] == dna[i - 1]:\n"
        "            cur_len += 1\n"
        "            max_len = max(max_len, cur_len)\n"
        "        else:\n"
        "            cur_len = 1\n"
        "    return max_len\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(String dna) {\n"
        "        if (dna.isEmpty()) return 0;\n"
        "        int maxLen = 1, curLen = 1;\n"
        "        for (int i = 1; i < dna.length(); i++) {\n"
        "            if (dna.charAt(i) == dna.charAt(i - 1)) {\n"
        "                curLen++;\n"
        "                maxLen = Math.max(maxLen, curLen);\n"
        "            } else {\n"
        "                curLen = 1;\n"
        "            }\n"
        "        }\n"
        "        return maxLen;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"dna": "ATTCGGGA"}, {"dna": "A"}, {"dna": "AAAA"},
        {"dna": "ACGT"}, {"dna": "AACCCGGGTTT"}, {"dna": "TTTTTTTTTT"},
        {"dna": "ATGATGATG"}, {"dna": "CCCCAAAAT"}, {"dna": "GCGCGCGC"},
        {"dna": "AABBCC"},
    ]
}

PROBLEMS_PART2["cses:1094"] = {
    "title": "Increasing Array",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1094",
    "source_id": "1094",
    "category": "Greedy",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "You are given an array of n integers. You want to modify the array so that it is increasing (each element is at least as large as the previous element). In one move, you can increase any element by 1. Find the minimum number of moves.",
    "examples": [
        {"input": "arr = [3,2,5,1,7]", "output": "5", "explanation": "Change to [3,3,5,5,7]: 1+0+0+4+0=5 moves."}
    ],
    "constraints": ["1 <= n <= 2*10^5", "1 <= arr[i] <= 10^9"],
    "solution_python": (
        "def solve(arr):\n"
        "    moves = 0\n"
        "    for i in range(1, len(arr)):\n"
        "        if arr[i] < arr[i - 1]:\n"
        "            moves += arr[i - 1] - arr[i]\n"
        "            arr[i] = arr[i - 1]\n"
        "    return moves\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static long solve(int[] arr) {\n"
        "        long moves = 0;\n"
        "        for (int i = 1; i < arr.length; i++) {\n"
        "            if (arr[i] < arr[i - 1]) {\n"
        "                moves += arr[i - 1] - arr[i];\n"
        "                arr[i] = arr[i - 1];\n"
        "            }\n"
        "        }\n"
        "        return moves;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [3, 2, 5, 1, 7]}, {"arr": [1, 2, 3, 4, 5]}, {"arr": [5, 4, 3, 2, 1]},
        {"arr": [1]}, {"arr": [1, 1, 1, 1]}, {"arr": [5, 1]},
        {"arr": [1, 2, 1, 2, 1]}, {"arr": [10, 1, 1, 1]},
        {"arr": [3, 3, 3]}, {"arr": [100, 50, 200, 150, 300]},
    ]
}

PROBLEMS_PART2["cses:1070"] = {
    "title": "Permutations",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1070",
    "source_id": "1070",
    "category": "Constructive",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "A permutation of integers 1, 2, ..., n is called beautiful if there are no adjacent elements whose difference is 1. Given n, construct a beautiful permutation if one exists, or return 'NO SOLUTION'.",
    "examples": [
        {"input": "n = 5", "output": "\"2 4 1 3 5\"", "explanation": "No adjacent elements differ by 1."},
        {"input": "n = 3", "output": "\"NO SOLUTION\"", "explanation": "No beautiful permutation exists for n=3."}
    ],
    "constraints": ["1 <= n <= 10^6"],
    "solution_python": (
        "def solve(n):\n"
        "    if n == 1:\n"
        "        return '1'\n"
        "    if n <= 3:\n"
        "        return 'NO SOLUTION'\n"
        "    evens = list(range(2, n + 1, 2))\n"
        "    odds = list(range(1, n + 1, 2))\n"
        "    return ' '.join(map(str, evens + odds))\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(int n) {\n"
        "        if (n == 1) return \"1\";\n"
        "        if (n <= 3) return \"NO SOLUTION\";\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i = 2; i <= n; i += 2) {\n"
        "            if (sb.length() > 0) sb.append(\" \");\n"
        "            sb.append(i);\n"
        "        }\n"
        "        for (int i = 1; i <= n; i += 2) {\n"
        "            sb.append(\" \").append(i);\n"
        "        }\n"
        "        return sb.toString();\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 5}, {"n": 3}, {"n": 1}, {"n": 2}, {"n": 4},
        {"n": 6}, {"n": 7}, {"n": 8}, {"n": 10}, {"n": 100},
    ]
}

PROBLEMS_PART2["cses:1071"] = {
    "title": "Number Spiral",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1071",
    "source_id": "1071",
    "category": "Mathematics",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "A number spiral is an infinite grid where the upper-left cell contains 1, and the numbers increase spiraling outward layer by layer. Given row y and column x, determine which number is in that cell.",
    "examples": [
        {"input": "y = 2, x = 3", "output": "8", "explanation": "Row 2, column 3 in the number spiral contains 8."}
    ],
    "constraints": ["1 <= y, x <= 10^9"],
    "solution_python": (
        "def solve(y, x):\n"
        "    layer = max(y, x)\n"
        "    if layer % 2 == 1:\n"
        "        if y == layer:\n"
        "            return layer * layer - x + 1\n"
        "        else:\n"
        "            return (layer - 1) * (layer - 1) + y\n"
        "    else:\n"
        "        if x == layer:\n"
        "            return layer * layer - y + 1\n"
        "        else:\n"
        "            return (layer - 1) * (layer - 1) + x\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static long solve(long y, long x) {\n"
        "        long layer = Math.max(y, x);\n"
        "        if (layer % 2 == 1) {\n"
        "            if (y == layer) return layer * layer - x + 1;\n"
        "            else return (layer - 1) * (layer - 1) + y;\n"
        "        } else {\n"
        "            if (x == layer) return layer * layer - y + 1;\n"
        "            else return (layer - 1) * (layer - 1) + x;\n"
        "        }\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"y": 2, "x": 3}, {"y": 1, "x": 1}, {"y": 4, "x": 2},
        {"y": 1, "x": 4}, {"y": 3, "x": 3}, {"y": 5, "x": 5},
        {"y": 2, "x": 2}, {"y": 1, "x": 2}, {"y": 3, "x": 1},
        {"y": 4, "x": 4},
    ]
}

PROBLEMS_PART2["cses:1072"] = {
    "title": "Two Knights",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1072",
    "source_id": "1072",
    "category": "Mathematics",
    "difficulty": "Medium",
    "companies": ["CSES"],
    "problem_statement": "For each k from 1 to n, count the number of ways to place two knights on a k x k chessboard so that they do not attack each other.",
    "examples": [
        {"input": "n = 8", "output": "\"0 6 28 96 252 550 1056 1848\"", "explanation": "For k=1: 0, k=2: 6, ... k=8: 1848"}
    ],
    "constraints": ["1 <= n <= 10000"],
    "solution_python": (
        "def solve(n):\n"
        "    results = []\n"
        "    for k in range(1, n + 1):\n"
        "        total = k * k * (k * k - 1) // 2\n"
        "        attacks = 0\n"
        "        if k >= 3:\n"
        "            attacks += 4 * (k - 1) * (k - 2)\n"
        "        results.append(total - attacks)\n"
        "    return ' '.join(map(str, results))\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(int n) {\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int k = 1; k <= n; k++) {\n"
        "            long total = (long) k * k * ((long) k * k - 1) / 2;\n"
        "            long attacks = 0;\n"
        "            if (k >= 3) attacks = 4L * (k - 1) * (k - 2);\n"
        "            if (sb.length() > 0) sb.append(\" \");\n"
        "            sb.append(total - attacks);\n"
        "        }\n"
        "        return sb.toString();\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 8}, {"n": 1}, {"n": 2}, {"n": 3}, {"n": 4},
        {"n": 5}, {"n": 6}, {"n": 7}, {"n": 10}, {"n": 15},
    ]
}

PROBLEMS_PART2["cses:1092"] = {
    "title": "Two Sets",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1092",
    "source_id": "1092",
    "category": "Mathematics",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "Your task is to divide the numbers 1, 2, ..., n into two sets of equal sum. Print the sizes of the sets and their elements, or 'NO' if not possible.",
    "examples": [
        {"input": "n = 7", "output": "\"YES\"", "explanation": "Sum 1..7 = 28. Set1: {1,6,7}=14, Set2: {2,3,4,5}=14."},
        {"input": "n = 6", "output": "\"NO\"", "explanation": "Sum 1..6 = 21, odd, cannot split."}
    ],
    "constraints": ["1 <= n <= 10^6"],
    "solution_python": (
        "def solve(n):\n"
        "    total = n * (n + 1) // 2\n"
        "    if total % 2 != 0:\n"
        "        return 'NO'\n"
        "    target = total // 2\n"
        "    set1 = []\n"
        "    remaining = target\n"
        "    for i in range(n, 0, -1):\n"
        "        if i <= remaining:\n"
        "            set1.append(i)\n"
        "            remaining -= i\n"
        "    set2 = [i for i in range(1, n + 1) if i not in set(set1)]\n"
        "    return 'YES'\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(int n) {\n"
        "        long total = (long) n * (n + 1) / 2;\n"
        "        if (total % 2 != 0) return \"NO\";\n"
        "        return \"YES\";\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 7}, {"n": 6}, {"n": 1}, {"n": 2}, {"n": 3},
        {"n": 4}, {"n": 8}, {"n": 10}, {"n": 15}, {"n": 100},
    ]
}

PROBLEMS_PART2["cses:1617"] = {
    "title": "Bit Strings",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1617",
    "source_id": "1617",
    "category": "Mathematics",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "Your task is to calculate the number of bit strings of length n. Since the answer can be large, output it modulo 10^9 + 7.",
    "examples": [
        {"input": "n = 3", "output": "8", "explanation": "2^3 = 8 bit strings: 000, 001, 010, 011, 100, 101, 110, 111."}
    ],
    "constraints": ["1 <= n <= 10^6"],
    "solution_python": (
        "def solve(n):\n"
        "    return pow(2, n, 10**9 + 7)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static long solve(int n) {\n"
        "        long MOD = 1000000007;\n"
        "        long result = 1;\n"
        "        long base = 2;\n"
        "        int exp = n;\n"
        "        while (exp > 0) {\n"
        "            if (exp % 2 == 1) result = result * base % MOD;\n"
        "            base = base * base % MOD;\n"
        "            exp /= 2;\n"
        "        }\n"
        "        return result;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 3}, {"n": 1}, {"n": 2}, {"n": 4}, {"n": 5},
        {"n": 10}, {"n": 20}, {"n": 30}, {"n": 64}, {"n": 100},
    ]
}

PROBLEMS_PART2["cses:1618"] = {
    "title": "Trailing Zeros",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1618",
    "source_id": "1618",
    "category": "Mathematics",
    "difficulty": "Easy",
    "companies": ["CSES", "Google"],
    "problem_statement": "Your task is to calculate the number of trailing zeros in the factorial n!.",
    "examples": [
        {"input": "n = 20", "output": "4", "explanation": "20! = 2432902008176640000, which has 4 trailing zeros."}
    ],
    "constraints": ["1 <= n <= 10^9"],
    "solution_python": (
        "def solve(n):\n"
        "    count = 0\n"
        "    power = 5\n"
        "    while power <= n:\n"
        "        count += n // power\n"
        "        power *= 5\n"
        "    return count\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int n) {\n"
        "        int count = 0;\n"
        "        long power = 5;\n"
        "        while (power <= n) {\n"
        "            count += n / power;\n"
        "            power *= 5;\n"
        "        }\n"
        "        return count;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 20}, {"n": 5}, {"n": 1}, {"n": 10}, {"n": 25},
        {"n": 100}, {"n": 1000}, {"n": 4}, {"n": 50}, {"n": 125},
    ]
}

PROBLEMS_PART2["cses:1754"] = {
    "title": "Coin Piles",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1754",
    "source_id": "1754",
    "category": "Mathematics",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "You have two coin piles containing a and b coins. On each move, you can remove either 1 coin from the first pile and 2 from the second, or 2 from the first and 1 from the second. Determine if both piles can be emptied.",
    "examples": [
        {"input": "a = 2, b = 1", "output": "\"YES\"", "explanation": "Remove 2 from a, 1 from b."},
        {"input": "a = 2, b = 2", "output": "\"NO\"", "explanation": "No valid sequence empties both."}
    ],
    "constraints": ["0 <= a, b <= 10^9"],
    "solution_python": (
        "def solve(a, b):\n"
        "    if (a + b) % 3 != 0:\n"
        "        return 'NO'\n"
        "    if a > 2 * b or b > 2 * a:\n"
        "        return 'NO'\n"
        "    return 'YES'\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(long a, long b) {\n"
        "        if ((a + b) % 3 != 0) return \"NO\";\n"
        "        if (a > 2 * b || b > 2 * a) return \"NO\";\n"
        "        return \"YES\";\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"a": 2, "b": 1}, {"a": 2, "b": 2}, {"a": 3, "b": 3},
        {"a": 0, "b": 0}, {"a": 1, "b": 0}, {"a": 6, "b": 3},
        {"a": 3, "b": 6}, {"a": 10, "b": 5}, {"a": 5, "b": 10},
        {"a": 100, "b": 200},
    ]
}

PROBLEMS_PART2["cses:1755"] = {
    "title": "Palindrome Reorder",
    "source_site": "cses",
    "source_url": "https://cses.fi/problemset/task/1755",
    "source_id": "1755",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["CSES"],
    "problem_statement": "Given a string, rearrange its characters to form a palindrome. If not possible, print 'NO SOLUTION'.",
    "examples": [
        {"input": "s = \"AAAACACBA\"", "output": "\"AACBCBCAA\"", "explanation": "One valid palindrome arrangement."}
    ],
    "constraints": ["1 <= len(s) <= 10^6"],
    "solution_python": (
        "def solve(s):\n"
        "    from collections import Counter\n"
        "    counts = Counter(s)\n"
        "    odd_chars = [ch for ch, cnt in counts.items() if cnt % 2 == 1]\n"
        "    if len(odd_chars) > 1:\n"
        "        return 'NO SOLUTION'\n"
        "    half = []\n"
        "    mid = ''\n"
        "    for ch in sorted(counts.keys()):\n"
        "        cnt = counts[ch]\n"
        "        half.extend([ch] * (cnt // 2))\n"
        "        if cnt % 2 == 1:\n"
        "            mid = ch\n"
        "    left = ''.join(half)\n"
        "    return left + mid + left[::-1]\n"
    ),
    "solution_java": (
        "import java.util.*;\n"
        "public class Solution {\n"
        "    public static String solve(String s) {\n"
        "        int[] counts = new int[256];\n"
        "        for (char c : s.toCharArray()) counts[c]++;\n"
        "        int oddCount = 0;\n"
        "        char oddChar = 0;\n"
        "        for (int i = 0; i < 256; i++) {\n"
        "            if (counts[i] % 2 == 1) { oddCount++; oddChar = (char) i; }\n"
        "        }\n"
        "        if (oddCount > 1) return \"NO SOLUTION\";\n"
        "        StringBuilder half = new StringBuilder();\n"
        "        for (int i = 0; i < 256; i++) {\n"
        "            for (int j = 0; j < counts[i] / 2; j++) half.append((char) i);\n"
        "        }\n"
        "        String left = half.toString();\n"
        "        String mid = oddCount == 1 ? String.valueOf(oddChar) : \"\";\n"
        "        return left + mid + half.reverse().toString();\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"s": "AAAACACBA"}, {"s": "A"}, {"s": "AB"},
        {"s": "ABA"}, {"s": "ABBA"}, {"s": "AABB"},
        {"s": "AAAA"}, {"s": "ABCBA"}, {"s": "ABCDE"},
        {"s": "AABBCC"},
    ]
}

# ---------------------------------------------------------------------------
# HACKERRANK (10 problems)
# ---------------------------------------------------------------------------

PROBLEMS_PART2["hackerrank:solve-me-first"] = {
    "title": "Solve Me First",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/solve-me-first/problem",
    "source_id": "solve-me-first",
    "category": "Basic",
    "difficulty": "Easy",
    "companies": ["HackerRank", "Amazon"],
    "problem_statement": "Complete the function solveMeFirst to compute the sum of two integers.",
    "examples": [{"input": "a = 2, b = 3", "output": "5", "explanation": "2 + 3 = 5"}],
    "constraints": ["1 <= a, b <= 1000"],
    "solution_python": "def solve(a, b):\n    return a + b\n",
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int a, int b) {\n"
        "        return a + b;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"a": 2, "b": 3}, {"a": 10, "b": 100}, {"a": 0, "b": 0},
        {"a": 1, "b": 1}, {"a": -5, "b": 5}, {"a": 1000, "b": 2000},
        {"a": -10, "b": -20}, {"a": 999, "b": 1}, {"a": 50, "b": 50},
        {"a": 123, "b": 456},
    ]
}

PROBLEMS_PART2["hackerrank:simple-array-sum"] = {
    "title": "Simple Array Sum",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/simple-array-sum/problem",
    "source_id": "simple-array-sum",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank", "Microsoft"],
    "problem_statement": "Given an array of integers, find the sum of its elements.",
    "examples": [{"input": "ar = [1,2,3,4,10,11]", "output": "31", "explanation": "1+2+3+4+10+11=31"}],
    "constraints": ["1 <= n <= 1000", "0 <= ar[i] <= 1000"],
    "solution_python": "def solve(ar):\n    return sum(ar)\n",
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] ar) {\n"
        "        int s = 0;\n"
        "        for (int x : ar) s += x;\n"
        "        return s;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"ar": [1, 2, 3, 4, 10, 11]}, {"ar": [1, 2, 3]}, {"ar": [0]},
        {"ar": [5, 5, 5]}, {"ar": [-1, -2, -3]}, {"ar": [100, 200, 300]},
        {"ar": [1, -1, 2, -2]}, {"ar": [1000]}, {"ar": [1, 2, 3, 4, 5]},
        {"ar": [5, 4, 3, 2, 1]},
    ]
}

PROBLEMS_PART2["hackerrank:compare-the-triplets"] = {
    "title": "Compare the Triplets",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/compare-the-triplets/problem",
    "source_id": "compare-the-triplets",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank", "Amazon"],
    "problem_statement": "Alice and Bob each created a problem and rated each other's solutions on three criteria. Compare each pair; Alice gets 1 point for each criterion where her value exceeds Bob's, and vice versa. Return their scores as [alice_score, bob_score].",
    "examples": [
        {"input": "a = [5,6,7], b = [3,6,10]", "output": "[1,1]", "explanation": "a[0]>b[0]: alice+1. a[1]==b[1]: tie. a[2]<b[2]: bob+1."}
    ],
    "constraints": ["1 <= a[i], b[i] <= 100"],
    "solution_python": (
        "def solve(a, b):\n"
        "    alice = sum(1 for x, y in zip(a, b) if x > y)\n"
        "    bob = sum(1 for x, y in zip(a, b) if y > x)\n"
        "    return [alice, bob]\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int[] solve(int[] a, int[] b) {\n"
        "        int alice = 0, bob = 0;\n"
        "        for (int i = 0; i < a.length; i++) {\n"
        "            if (a[i] > b[i]) alice++;\n"
        "            else if (b[i] > a[i]) bob++;\n"
        "        }\n"
        "        return new int[]{alice, bob};\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"a": [5, 6, 7], "b": [3, 6, 10]},
        {"a": [1, 2, 3], "b": [3, 2, 1]},
        {"a": [10, 10, 10], "b": [10, 10, 10]},
        {"a": [1, 1, 1], "b": [2, 2, 2]},
        {"a": [100, 1, 50], "b": [1, 100, 50]},
        {"a": [17, 28, 30], "b": [99, 16, 8]},
        {"a": [5, 5, 5], "b": [5, 5, 5]},
        {"a": [1, 2, 3], "b": [1, 2, 3]},
        {"a": [50, 50, 50], "b": [25, 75, 50]},
        {"a": [3, 3, 3], "b": [1, 1, 1]},
    ]
}

PROBLEMS_PART2["hackerrank:a-very-big-sum"] = {
    "title": "A Very Big Sum",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/a-very-big-sum/problem",
    "source_id": "a-very-big-sum",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank"],
    "problem_statement": "You are required to calculate and print the sum of the elements in an array, keeping in mind that some of those integers may be quite large.",
    "examples": [{"input": "ar = [1000000001,1000000002,1000000003,1000000004,1000000005]", "output": "5000000015", "explanation": "Sum of all elements."}],
    "constraints": ["1 <= n <= 10", "0 <= ar[i] <= 10^10"],
    "solution_python": "def solve(ar):\n    return sum(ar)\n",
    "solution_java": (
        "public class Solution {\n"
        "    public static long solve(long[] ar) {\n"
        "        long s = 0;\n"
        "        for (long x : ar) s += x;\n"
        "        return s;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"ar": [1000000001, 1000000002, 1000000003, 1000000004, 1000000005]},
        {"ar": [1, 2, 3]}, {"ar": [0]}, {"ar": [10000000000]},
        {"ar": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
        {"ar": [5000000000, 5000000000]}, {"ar": [100, 200]},
        {"ar": [9999999999, 1]}, {"ar": [0, 0, 0]},
        {"ar": [123456789, 987654321]},
    ]
}

PROBLEMS_PART2["hackerrank:diagonal-difference"] = {
    "title": "Diagonal Difference",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/diagonal-difference/problem",
    "source_id": "diagonal-difference",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank", "Amazon"],
    "problem_statement": "Given a square matrix, calculate the absolute difference between the sums of its two diagonals.",
    "examples": [
        {"input": "arr = [[11,2,4],[4,5,6],[10,8,-12]]", "output": "15", "explanation": "Primary diagonal: 11+5+(-12)=4. Secondary: 4+5+10=19. |4-19|=15."}
    ],
    "constraints": ["-100 <= arr[i][j] <= 100", "1 <= n <= 100"],
    "solution_python": (
        "def solve(arr):\n"
        "    n = len(arr)\n"
        "    d1 = sum(arr[i][i] for i in range(n))\n"
        "    d2 = sum(arr[i][n - 1 - i] for i in range(n))\n"
        "    return abs(d1 - d2)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[][] arr) {\n"
        "        int n = arr.length;\n"
        "        int d1 = 0, d2 = 0;\n"
        "        for (int i = 0; i < n; i++) {\n"
        "            d1 += arr[i][i];\n"
        "            d2 += arr[i][n - 1 - i];\n"
        "        }\n"
        "        return Math.abs(d1 - d2);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [[11, 2, 4], [4, 5, 6], [10, 8, -12]]},
        {"arr": [[1, 2], [3, 4]]},
        {"arr": [[1]]},
        {"arr": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]},
        {"arr": [[5, 5], [5, 5]]},
        {"arr": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
        {"arr": [[-1, -2], [-3, -4]]},
        {"arr": [[10, 20, 30], [40, 50, 60], [70, 80, 90]]},
        {"arr": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]},
        {"arr": [[100, -100], [-100, 100]]},
    ]
}

PROBLEMS_PART2["hackerrank:plus-minus"] = {
    "title": "Plus Minus",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/plus-minus/problem",
    "source_id": "plus-minus",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank"],
    "problem_statement": "Given an array of integers, calculate the ratios of its elements that are positive, negative, and zero. Return the results as a list of three floats, each rounded to 6 decimal places.",
    "examples": [
        {"input": "arr = [1,1,0,-1,-1]", "output": "[0.4,0.4,0.2]", "explanation": "2/5 positive, 2/5 negative, 1/5 zero."}
    ],
    "constraints": ["0 < n <= 100", "-100 <= arr[i] <= 100"],
    "solution_python": (
        "def solve(arr):\n"
        "    n = len(arr)\n"
        "    pos = sum(1 for x in arr if x > 0) / n\n"
        "    neg = sum(1 for x in arr if x < 0) / n\n"
        "    zero = sum(1 for x in arr if x == 0) / n\n"
        "    return [round(pos, 6), round(neg, 6), round(zero, 6)]\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static double[] solve(int[] arr) {\n"
        "        int n = arr.length;\n"
        "        int pos = 0, neg = 0, zero = 0;\n"
        "        for (int x : arr) {\n"
        "            if (x > 0) pos++;\n"
        "            else if (x < 0) neg++;\n"
        "            else zero++;\n"
        "        }\n"
        "        return new double[]{(double) pos / n, (double) neg / n, (double) zero / n};\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 1, 0, -1, -1]},
        {"arr": [1, 2, 3]},
        {"arr": [-1, -2, -3]},
        {"arr": [0, 0, 0]},
        {"arr": [1]},
        {"arr": [-1]},
        {"arr": [0]},
        {"arr": [1, -1, 0, 1, -1]},
        {"arr": [5, 5, 5, 5, 5, -5, -5, -5, 0, 0]},
        {"arr": [100, -100]},
    ]
}

PROBLEMS_PART2["hackerrank:staircase"] = {
    "title": "Staircase",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/staircase/problem",
    "source_id": "staircase",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["HackerRank"],
    "problem_statement": "Print a right-aligned staircase of size n using '#' symbols. Each step has one more '#' than the previous one, with spaces for alignment. Return the staircase as a single string with newlines.",
    "examples": [
        {"input": "n = 4", "output": "\"   #\\n  ##\\n ###\\n####\"", "explanation": "Right-aligned staircase with 4 steps."}
    ],
    "constraints": ["0 < n <= 100"],
    "solution_python": (
        "def solve(n):\n"
        "    lines = []\n"
        "    for i in range(1, n + 1):\n"
        "        lines.append(' ' * (n - i) + '#' * i)\n"
        "    return '\\n'.join(lines)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(int n) {\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i = 1; i <= n; i++) {\n"
        "            if (i > 1) sb.append(\"\\n\");\n"
        "            for (int j = 0; j < n - i; j++) sb.append(\" \");\n"
        "            for (int j = 0; j < i; j++) sb.append(\"#\");\n"
        "        }\n"
        "        return sb.toString();\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 4}, {"n": 1}, {"n": 2}, {"n": 3}, {"n": 5},
        {"n": 6}, {"n": 7}, {"n": 8}, {"n": 9}, {"n": 10},
    ]
}

PROBLEMS_PART2["hackerrank:mini-max-sum"] = {
    "title": "Mini-Max Sum",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/mini-max-sum/problem",
    "source_id": "mini-max-sum",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank", "Amazon"],
    "problem_statement": "Given five positive integers, find the minimum and maximum values that can be calculated by summing exactly four of the five integers. Return [min_sum, max_sum].",
    "examples": [
        {"input": "arr = [1,2,3,4,5]", "output": "[10,14]", "explanation": "Min=1+2+3+4=10, Max=2+3+4+5=14."}
    ],
    "constraints": ["The array always has exactly 5 positive integers.", "1 <= arr[i] <= 10^9"],
    "solution_python": (
        "def solve(arr):\n"
        "    total = sum(arr)\n"
        "    return [total - max(arr), total - min(arr)]\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static long[] solve(int[] arr) {\n"
        "        long total = 0;\n"
        "        int min = arr[0], max = arr[0];\n"
        "        for (int x : arr) {\n"
        "            total += x;\n"
        "            if (x < min) min = x;\n"
        "            if (x > max) max = x;\n"
        "        }\n"
        "        return new long[]{total - max, total - min};\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, 4, 5]},
        {"arr": [5, 5, 5, 5, 5]},
        {"arr": [1, 1, 1, 1, 1000000000]},
        {"arr": [10, 20, 30, 40, 50]},
        {"arr": [7, 69, 2, 221, 8974]},
        {"arr": [256741038, 623958417, 467905213, 714532089, 938071625]},
        {"arr": [100, 200, 300, 400, 500]},
        {"arr": [1, 3, 5, 7, 9]},
        {"arr": [2, 2, 2, 2, 2]},
        {"arr": [999999999, 999999999, 999999999, 999999999, 999999999]},
    ]
}

PROBLEMS_PART2["hackerrank:birthday-cake-candles"] = {
    "title": "Birthday Cake Candles",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/birthday-cake-candles/problem",
    "source_id": "birthday-cake-candles",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["HackerRank"],
    "problem_statement": "You are in charge of the cake for a child's birthday. The cake has candles of various heights. The tallest candles can be blown out. Return the count of candles that are tallest.",
    "examples": [
        {"input": "candles = [3,2,1,3]", "output": "2", "explanation": "The tallest candles are 3. There are 2 of them."}
    ],
    "constraints": ["1 <= n <= 10^5", "1 <= candles[i] <= 10^7"],
    "solution_python": (
        "def solve(candles):\n"
        "    mx = max(candles)\n"
        "    return candles.count(mx)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] candles) {\n"
        "        int max = candles[0], count = 0;\n"
        "        for (int c : candles) if (c > max) max = c;\n"
        "        for (int c : candles) if (c == max) count++;\n"
        "        return count;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"candles": [3, 2, 1, 3]}, {"candles": [1, 2, 3, 3]},
        {"candles": [1]}, {"candles": [5, 5, 5, 5]},
        {"candles": [1, 1, 1, 1, 1]}, {"candles": [10]},
        {"candles": [7, 4, 7, 2, 7, 1]}, {"candles": [1, 2, 3, 4, 5]},
        {"candles": [100, 100, 50, 100]}, {"candles": [1, 10000000]},
    ]
}

PROBLEMS_PART2["hackerrank:time-conversion"] = {
    "title": "Time Conversion",
    "source_site": "hackerrank",
    "source_url": "https://www.hackerrank.com/challenges/time-conversion/problem",
    "source_id": "time-conversion",
    "category": "Strings",
    "difficulty": "Easy",
    "companies": ["Amazon", "Google", "HackerRank"],
    "problem_statement": "Given a time in 12-hour AM/PM format, convert it to military (24-hour) time.",
    "examples": [
        {"input": "s = \"07:05:45PM\"", "output": "\"19:05:45\"", "explanation": "7:05:45 PM = 19:05:45 in 24-hour format."},
        {"input": "s = \"12:00:00AM\"", "output": "\"00:00:00\"", "explanation": "12 AM is midnight."}
    ],
    "constraints": ["All input times are valid."],
    "solution_python": (
        "def solve(s):\n"
        "    period = s[-2:]\n"
        "    hour = int(s[:2])\n"
        "    rest = s[2:-2]\n"
        "    if period == 'AM':\n"
        "        if hour == 12: hour = 0\n"
        "    else:\n"
        "        if hour != 12: hour += 12\n"
        "    return f'{hour:02d}{rest}'\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static String solve(String s) {\n"
        "        String period = s.substring(s.length() - 2);\n"
        "        int hour = Integer.parseInt(s.substring(0, 2));\n"
        "        String rest = s.substring(2, s.length() - 2);\n"
        "        if (period.equals(\"AM\")) {\n"
        "            if (hour == 12) hour = 0;\n"
        "        } else {\n"
        "            if (hour != 12) hour += 12;\n"
        "        }\n"
        "        return String.format(\"%02d%s\", hour, rest);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"s": "07:05:45PM"}, {"s": "12:00:00AM"}, {"s": "12:00:00PM"},
        {"s": "01:00:00AM"}, {"s": "01:00:00PM"}, {"s": "11:59:59PM"},
        {"s": "11:59:59AM"}, {"s": "06:40:03AM"}, {"s": "04:15:30PM"},
        {"s": "12:45:54PM"},
    ]
}

# ---------------------------------------------------------------------------
# GEEKSFORGEEKS (13 problems)
# ---------------------------------------------------------------------------

PROBLEMS_PART2["geeksforgeeks:kadanes-algorithm"] = {
    "title": "Kadane's Algorithm",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/kadanes-algorithm-1587115620/1",
    "source_id": "kadanes-algorithm",
    "category": "Dynamic Programming",
    "difficulty": "Medium",
    "companies": ["Amazon", "Microsoft", "Flipkart", "Google"],
    "problem_statement": "Given an integer array arr[]. Find the contiguous sub-array (containing at least one number) which has the maximum sum and return its sum.",
    "examples": [{"input": "arr = [1,2,3,-2,5]", "output": "9", "explanation": "Max subarray: [1,2,3,-2,5] sum=9"}],
    "constraints": ["1 <= arr.size() <= 10^5", "-10^7 <= arr[i] <= 10^7"],
    "solution_python": (
        "def solve(arr):\n"
        "    max_so_far = arr[0]\n"
        "    curr_max = arr[0]\n"
        "    for i in range(1, len(arr)):\n"
        "        curr_max = max(arr[i], curr_max + arr[i])\n"
        "        max_so_far = max(max_so_far, curr_max)\n"
        "    return max_so_far\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] arr) {\n"
        "        int maxSoFar = arr[0], currMax = arr[0];\n"
        "        for (int i = 1; i < arr.length; i++) {\n"
        "            currMax = Math.max(arr[i], currMax + arr[i]);\n"
        "            maxSoFar = Math.max(maxSoFar, currMax);\n"
        "        }\n"
        "        return maxSoFar;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, -2, 5]}, {"arr": [-1, -2, -3, -4]},
        {"arr": [5]}, {"arr": [1, -1, 1, -1, 1]}, {"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]},
        {"arr": [1, 2, 3, 4, 5]}, {"arr": [-1]}, {"arr": [0, 0, 0]},
        {"arr": [10, -5, 10, -5, 10]}, {"arr": [-3, -2, -1]},
    ]
}

PROBLEMS_PART2["geeksforgeeks:subarray-with-given-sum-1587115621"] = {
    "title": "Subarray With Given Sum",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/subarray-with-given-sum-1587115621/1",
    "source_id": "subarray-with-given-sum-1587115621",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft"],
    "problem_statement": "Given an unsorted array of non-negative integers and a target sum, find a subarray that adds to the given sum. Return the 1-based start and end indices, or [-1] if not found.",
    "examples": [{"input": "arr = [1,2,3,7,5], target = 12", "output": "[2,4]", "explanation": "arr[2..4] = 2+3+7 = 12."}],
    "constraints": ["1 <= arr.size() <= 10^5", "0 <= arr[i] <= 10^4", "0 <= target <= 10^7"],
    "solution_python": (
        "def solve(arr, target):\n"
        "    curr_sum = 0\n"
        "    start = 0\n"
        "    for end in range(len(arr)):\n"
        "        curr_sum += arr[end]\n"
        "        while curr_sum > target and start <= end:\n"
        "            curr_sum -= arr[start]\n"
        "            start += 1\n"
        "        if curr_sum == target:\n"
        "            return [start + 1, end + 1]\n"
        "    return [-1]\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int[] solve(int[] arr, int target) {\n"
        "        int currSum = 0, start = 0;\n"
        "        for (int end = 0; end < arr.length; end++) {\n"
        "            currSum += arr[end];\n"
        "            while (currSum > target && start <= end) {\n"
        "                currSum -= arr[start];\n"
        "                start++;\n"
        "            }\n"
        "            if (currSum == target) return new int[]{start + 1, end + 1};\n"
        "        }\n"
        "        return new int[]{-1};\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, 7, 5], "target": 12},
        {"arr": [1, 2, 3, 4, 5], "target": 15},
        {"arr": [5, 3, 2], "target": 10},
        {"arr": [1, 2, 3], "target": 6},
        {"arr": [1, 2, 3], "target": 5},
        {"arr": [4], "target": 4},
        {"arr": [4], "target": 5},
        {"arr": [1, 1, 1, 1, 1], "target": 3},
        {"arr": [10, 20, 30], "target": 50},
        {"arr": [1, 2, 3, 4, 5], "target": 9},
    ]
}

PROBLEMS_PART2["geeksforgeeks:missing-number-in-array1416"] = {
    "title": "Missing Number In Array",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/missing-number-in-array1416/1",
    "source_id": "missing-number-in-array1416",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft", "Google"],
    "problem_statement": "Given an array of size n-1 containing distinct integers from 1 to n, find the missing number.",
    "examples": [{"input": "n = 5, arr = [1,2,3,5]", "output": "4", "explanation": "4 is missing from 1..5."}],
    "constraints": ["2 <= n <= 10^6", "1 <= arr[i] <= n"],
    "solution_python": (
        "def solve(n, arr):\n"
        "    return n * (n + 1) // 2 - sum(arr)\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int n, int[] arr) {\n"
        "        long total = (long) n * (n + 1) / 2;\n"
        "        long sum = 0;\n"
        "        for (int x : arr) sum += x;\n"
        "        return (int)(total - sum);\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"n": 5, "arr": [1, 2, 3, 5]}, {"n": 2, "arr": [1]},
        {"n": 2, "arr": [2]}, {"n": 3, "arr": [1, 3]},
        {"n": 4, "arr": [4, 2, 1]}, {"n": 6, "arr": [1, 2, 3, 5, 6]},
        {"n": 7, "arr": [1, 2, 3, 4, 5, 7]}, {"n": 8, "arr": [8, 7, 6, 5, 4, 3, 2]},
        {"n": 10, "arr": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
        {"n": 3, "arr": [2, 3]},
    ]
}

PROBLEMS_PART2["geeksforgeeks:parenthesis-checker2705"] = {
    "title": "Parenthesis Checker",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/parenthesis-checker2705/1",
    "source_id": "parenthesis-checker2705",
    "category": "Stack",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft", "Flipkart", "Oyo"],
    "problem_statement": "Given an expression string x, examine whether the pairs and the orders of '{', '}', '(', ')', '[', ']' are correct.",
    "examples": [
        {"input": "s = \"{[()]}\"", "output": "true", "explanation": "All brackets matched correctly."},
        {"input": "s = \"()\"", "output": "true", "explanation": "Parentheses matched."},
        {"input": "s = \"([]\"", "output": "false", "explanation": "Unmatched opening parenthesis."}
    ],
    "constraints": ["1 <= |x| <= 10^5"],
    "solution_python": (
        "def solve(s):\n"
        "    stack = []\n"
        "    mapping = {')': '(', '}': '{', ']': '['}\n"
        "    for char in s:\n"
        "        if char in mapping:\n"
        "            top = stack.pop() if stack else '#'\n"
        "            if mapping[char] != top: return False\n"
        "        else:\n"
        "            stack.append(char)\n"
        "    return len(stack) == 0\n"
    ),
    "solution_java": (
        "import java.util.*;\n"
        "public class Solution {\n"
        "    public static boolean solve(String s) {\n"
        "        Stack<Character> stack = new Stack<>();\n"
        "        for (char c : s.toCharArray()) {\n"
        "            if (c == '(' || c == '{' || c == '[') stack.push(c);\n"
        "            else {\n"
        "                if (stack.isEmpty()) return false;\n"
        "                char top = stack.pop();\n"
        "                if (c == ')' && top != '(') return false;\n"
        "                if (c == '}' && top != '{') return false;\n"
        "                if (c == ']' && top != '[') return false;\n"
        "            }\n"
        "        }\n"
        "        return stack.isEmpty();\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"s": "{[()]}"}, {"s": "()"}, {"s": "([]"},
        {"s": "()[]{}"}, {"s": "(]"}, {"s": "([)]"},
        {"s": "{"}, {"s": "}"}, {"s": "((()))"},
        {"s": "({[]})"},
    ]
}

PROBLEMS_PART2["geeksforgeeks:find-duplicates-in-an-array"] = {
    "title": "Find Duplicates In An Array",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/find-duplicates-in-an-array/1",
    "source_id": "find-duplicates-in-an-array",
    "category": "Arrays",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft"],
    "problem_statement": "Given an array of integers where elements are in the range [0, n-1], find all elements that appear more than once. Return them in sorted order. If no duplicates, return [-1].",
    "examples": [{"input": "arr = [2,3,1,2,3]", "output": "[2,3]", "explanation": "2 and 3 appear more than once."}],
    "constraints": ["1 <= n <= 10^5", "0 <= arr[i] <= n-1"],
    "solution_python": (
        "def solve(arr):\n"
        "    from collections import Counter\n"
        "    counts = Counter(arr)\n"
        "    result = sorted([k for k, v in counts.items() if v > 1])\n"
        "    return result if result else [-1]\n"
    ),
    "solution_java": (
        "import java.util.*;\n"
        "public class Solution {\n"
        "    public static int[] solve(int[] arr) {\n"
        "        Map<Integer, Integer> map = new HashMap<>();\n"
        "        for (int x : arr) map.put(x, map.getOrDefault(x, 0) + 1);\n"
        "        List<Integer> res = new ArrayList<>();\n"
        "        for (Map.Entry<Integer, Integer> e : map.entrySet()) {\n"
        "            if (e.getValue() > 1) res.add(e.getKey());\n"
        "        }\n"
        "        Collections.sort(res);\n"
        "        if (res.isEmpty()) return new int[]{-1};\n"
        "        int[] result = new int[res.size()];\n"
        "        for (int i = 0; i < res.size(); i++) result[i] = res.get(i);\n"
        "        return result;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [2, 3, 1, 2, 3]}, {"arr": [0, 1, 2, 3]},
        {"arr": [1, 1, 1]}, {"arr": [0, 0, 0, 0]},
        {"arr": [5, 4, 3, 2, 1, 5, 4]}, {"arr": [1, 2, 3, 4, 5]},
        {"arr": [0]}, {"arr": [1, 1, 2, 2, 3, 3]},
        {"arr": [3, 3, 3, 3]}, {"arr": [2, 1]},
    ]
}

PROBLEMS_PART2["geeksforgeeks:kadanes-algorithm-1587115620"] = {
    "title": "Maximum Subarray Sum",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/kadanes-algorithm-1587115620/1",
    "source_id": "kadanes-algorithm-1587115620",
    "category": "Dynamic Programming",
    "difficulty": "Medium",
    "companies": ["Amazon", "Microsoft", "Google", "Flipkart"],
    "problem_statement": "Given an array arr[] of integers, find the contiguous subarray which has the maximum sum and return its sum.",
    "examples": [{"input": "arr = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "Subarray [4,-1,2,1] has sum 6."}],
    "constraints": ["1 <= arr.size() <= 10^5", "-10^7 <= arr[i] <= 10^7"],
    "solution_python": (
        "def solve(arr):\n"
        "    max_sum = arr[0]\n"
        "    cur = arr[0]\n"
        "    for i in range(1, len(arr)):\n"
        "        cur = max(arr[i], cur + arr[i])\n"
        "        max_sum = max(max_sum, cur)\n"
        "    return max_sum\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] arr) {\n"
        "        int maxSum = arr[0], cur = arr[0];\n"
        "        for (int i = 1; i < arr.length; i++) {\n"
        "            cur = Math.max(arr[i], cur + arr[i]);\n"
        "            maxSum = Math.max(maxSum, cur);\n"
        "        }\n"
        "        return maxSum;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, {"arr": [1, 2, 3, 4, 5]},
        {"arr": [-1, -2, -3]}, {"arr": [5]}, {"arr": [-5]},
        {"arr": [1, -1, 1, -1, 1]}, {"arr": [10, -5, 10]},
        {"arr": [-2, -1]}, {"arr": [0, 0, 0]},
        {"arr": [3, -2, 5, -1]},
    ]
}

PROBLEMS_PART2["geeksforgeeks:minimum-number-of-jumps-1587115620"] = {
    "title": "Minimum Number of Jumps",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/minimum-number-of-jumps-1587115620/1",
    "source_id": "minimum-number-of-jumps-1587115620",
    "category": "Greedy",
    "difficulty": "Medium",
    "companies": ["Amazon", "Microsoft", "Google"],
    "problem_statement": "Given an array where each element represents the max number of steps you can jump forward, return the minimum number of jumps to reach the end. Return -1 if unreachable.",
    "examples": [{"input": "arr = [1,3,5,8,9,2,6,7,6,8,9]", "output": "3", "explanation": "Jump 1->3->9->end."}],
    "constraints": ["1 <= arr.size() <= 10^5", "0 <= arr[i] <= 10^5"],
    "solution_python": (
        "def solve(arr):\n"
        "    n = len(arr)\n"
        "    if n <= 1: return 0\n"
        "    if arr[0] == 0: return -1\n"
        "    jumps = 1\n"
        "    max_reach = arr[0]\n"
        "    steps = arr[0]\n"
        "    for i in range(1, n):\n"
        "        if i == n - 1: return jumps\n"
        "        max_reach = max(max_reach, i + arr[i])\n"
        "        steps -= 1\n"
        "        if steps == 0:\n"
        "            jumps += 1\n"
        "            if i >= max_reach: return -1\n"
        "            steps = max_reach - i\n"
        "    return -1\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] arr) {\n"
        "        int n = arr.length;\n"
        "        if (n <= 1) return 0;\n"
        "        if (arr[0] == 0) return -1;\n"
        "        int jumps = 1, maxReach = arr[0], steps = arr[0];\n"
        "        for (int i = 1; i < n; i++) {\n"
        "            if (i == n - 1) return jumps;\n"
        "            maxReach = Math.max(maxReach, i + arr[i]);\n"
        "            steps--;\n"
        "            if (steps == 0) {\n"
        "                jumps++;\n"
        "                if (i >= maxReach) return -1;\n"
        "                steps = maxReach - i;\n"
        "            }\n"
        "        }\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 3, 5, 8, 9, 2, 6, 7, 6, 8, 9]},
        {"arr": [1, 4, 3, 2, 6, 7]},
        {"arr": [0, 10, 20]},
        {"arr": [1]},
        {"arr": [2, 3, 1, 1, 4]},
        {"arr": [1, 1, 1, 1, 1]},
        {"arr": [5, 4, 3, 2, 1]},
        {"arr": [10, 0, 0, 0, 0]},
        {"arr": [1, 0]},
        {"arr": [2, 1, 0, 3]},
    ]
}

PROBLEMS_PART2["geeksforgeeks:nth-node-from-end-of-linked-list"] = {
    "title": "Nth Node From End",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/nth-node-from-end-of-linked-list/1",
    "source_id": "nth-node-from-end-of-linked-list",
    "category": "Linked List",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft", "Flipkart"],
    "problem_statement": "Given a linked list (represented as an array) and an integer n, find the nth node from the end. Return its data.",
    "examples": [{"input": "arr = [1,2,3,4,5,6,7,8,9], n = 2", "output": "8", "explanation": "2nd from end is 8."}],
    "constraints": ["1 <= size of linked list <= 10^3", "1 <= n <= size"],
    "solution_python": (
        "def solve(arr, n):\n"
        "    return arr[len(arr) - n]\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static int solve(int[] arr, int n) {\n"
        "        return arr[arr.length - n];\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, 4, 5, 6, 7, 8, 9], "n": 2},
        {"arr": [10, 5, 100, 5], "n": 4},
        {"arr": [1], "n": 1},
        {"arr": [1, 2], "n": 1},
        {"arr": [1, 2], "n": 2},
        {"arr": [5, 10, 15, 20, 25], "n": 3},
        {"arr": [3, 6, 9], "n": 1},
        {"arr": [7, 14, 21, 28], "n": 2},
        {"arr": [100, 200, 300], "n": 3},
        {"arr": [1, 2, 3, 4, 5], "n": 5},
    ]
}

PROBLEMS_PART2["geeksforgeeks:detect-loop-in-linked-list"] = {
    "title": "Detect Loop",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/detect-loop-in-linked-list/1",
    "source_id": "detect-loop-in-linked-list",
    "category": "Linked List",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft", "Samsung"],
    "problem_statement": "Given a linked list (represented as an array of values and a loop_pos indicating where the tail connects back, or -1 for no loop), determine if there is a loop.",
    "examples": [{"input": "arr = [1,2,3,4,5], loop_pos = 2", "output": "true", "explanation": "Tail connects to node at position 2 (value 3)."}],
    "constraints": ["1 <= n <= 10^4"],
    "solution_python": (
        "def solve(arr, loop_pos):\n"
        "    return loop_pos >= 0\n"
    ),
    "solution_java": (
        "public class Solution {\n"
        "    public static boolean solve(int[] arr, int loopPos) {\n"
        "        return loopPos >= 0;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, 4, 5], "loop_pos": 2},
        {"arr": [1, 2, 3], "loop_pos": -1},
        {"arr": [1], "loop_pos": 0},
        {"arr": [1], "loop_pos": -1},
        {"arr": [1, 2], "loop_pos": 0},
        {"arr": [1, 2, 3, 4], "loop_pos": 3},
        {"arr": [1, 2, 3, 4, 5], "loop_pos": -1},
        {"arr": [10, 20, 30], "loop_pos": 1},
        {"arr": [5, 10], "loop_pos": -1},
        {"arr": [1, 2, 3, 4, 5, 6], "loop_pos": 0},
    ]
}

PROBLEMS_PART2["geeksforgeeks:reverse-a-linked-list"] = {
    "title": "Reverse A Linked List",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/reverse-a-linked-list/1",
    "source_id": "reverse-a-linked-list",
    "category": "Linked List",
    "difficulty": "Easy",
    "companies": ["Amazon", "Microsoft", "Accolite", "Adobe"],
    "problem_statement": "Given a linked list (represented as an array), reverse it and return the reversed list.",
    "examples": [{"input": "arr = [1,2,3,4,5]", "output": "[5,4,3,2,1]", "explanation": "Reversed linked list."}],
    "constraints": ["1 <= size of linked list <= 10^5"],
    "solution_python": "def solve(arr):\n    return arr[::-1]\n",
    "solution_java": (
        "public class Solution {\n"
        "    public static int[] solve(int[] arr) {\n"
        "        int[] res = new int[arr.length];\n"
        "        for (int i = 0; i < arr.length; i++) {\n"
        "            res[i] = arr[arr.length - 1 - i];\n"
        "        }\n"
        "        return res;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, 4, 5]}, {"arr": [1]}, {"arr": [1, 2]},
        {"arr": [5, 4, 3, 2, 1]}, {"arr": [10, 20, 30]},
        {"arr": [100]}, {"arr": [1, 1, 1]}, {"arr": [7, 14, 21, 28]},
        {"arr": [3, 6, 9, 12, 15]}, {"arr": [42, 17]},
    ]
}

PROBLEMS_PART2["geeksforgeeks:left-view-of-binary-tree"] = {
    "title": "Left View Of Binary Tree",
    "source_site": "geeksforgeeks",
    "source_url": "https://www.geeksforgeeks.org/problems/left-view-of-binary-tree/1",
    "source_id": "left-view-of-binary-tree",
    "category": "Trees",
    "difficulty": "Easy",
    "companies": ["Amazon", "Flipkart", "Oyo"],
    "problem_statement": "Given a binary tree represented as a level-order array (with -1 for null nodes), print the left view — the first node visible at each level when looking from the left side.",
    "examples": [{"input": "arr = [1,2,3,4,5,-1,6]", "output": "[1,2,4]", "explanation": "Left view: level 0: 1, level 1: 2, level 2: 4."}],
    "constraints": ["0 <= number of nodes <= 100", "1 <= node values <= 10^5"],
    "solution_python": (
        "def solve(arr):\n"
        "    if not arr or arr[0] == -1:\n"
        "        return []\n"
        "    result = []\n"
        "    level = [0]\n"
        "    while level:\n"
        "        result.append(arr[level[0]])\n"
        "        next_level = []\n"
        "        for idx in level:\n"
        "            left = 2 * idx + 1\n"
        "            right = 2 * idx + 2\n"
        "            if left < len(arr) and arr[left] != -1:\n"
        "                next_level.append(left)\n"
        "            if right < len(arr) and arr[right] != -1:\n"
        "                next_level.append(right)\n"
        "        level = next_level\n"
        "    return result\n"
    ),
    "solution_java": (
        "import java.util.*;\n"
        "public class Solution {\n"
        "    public static int[] solve(int[] arr) {\n"
        "        if (arr.length == 0 || arr[0] == -1) return new int[0];\n"
        "        List<Integer> result = new ArrayList<>();\n"
        "        List<Integer> level = new ArrayList<>();\n"
        "        level.add(0);\n"
        "        while (!level.isEmpty()) {\n"
        "            result.add(arr[level.get(0)]);\n"
        "            List<Integer> nextLevel = new ArrayList<>();\n"
        "            for (int idx : level) {\n"
        "                int left = 2 * idx + 1;\n"
        "                int right = 2 * idx + 2;\n"
        "                if (left < arr.length && arr[left] != -1) nextLevel.add(left);\n"
        "                if (right < arr.length && arr[right] != -1) nextLevel.add(right);\n"
        "            }\n"
        "            level = nextLevel;\n"
        "        }\n"
        "        int[] res = new int[result.size()];\n"
        "        for (int i = 0; i < result.size(); i++) res[i] = result.get(i);\n"
        "        return res;\n"
        "    }\n"
        "}\n"
    ),
    "test_inputs": [
        {"arr": [1, 2, 3, 4, 5, -1, 6]}, {"arr": [1]},
        {"arr": [1, 2, -1]}, {"arr": [1, -1, 3]},
        {"arr": [1, 2, 3]}, {"arr": [1, 2, 3, 4, -1, -1, 7]},
        {"arr": [10, 20, 30, 40, 50, 60, 70]},
        {"arr": [5, 3, 8, 1, 4, 7, 9]},
        {"arr": [1, 2, 3, -1, 5, 6, -1]},
        {"arr": [100, 50, 150, 25, 75, 125, 175]},
    ]
}

print(f"Loaded {len(PROBLEMS_PART2)} problems in part 2")
