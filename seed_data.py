import time
from datetime import datetime
from utils.db import get_db_connection
from utils.embedding_helper import generate_embedding

# 15 Realistic Study Resources covering various core CS subjects and difficulties
SAMPLE_RESOURCES = [
    {
        "title": "Understanding Processes and Pipes in Operating Systems",
        "subject": "Operating Systems",
        "topic": "Process Management & Inter-Process Communication",
        "difficulty": "Beginner",
        "resource_type": "Article",
        "description": "A beginner-friendly breakdown explaining how operating systems create processes, manage process states, and allow child and parent processes to communicate using POSIX pipes.",
        "content": "A process is a program in execution. In Unix-like operating systems, processes communicate using inter-process communication (IPC) primitives. A pipe is a unidirectional data channel that allows one process to send bytes to another process using standard file descriptors.",
        "tags": ["operating systems", "processes", "pipes", "ipc", "posix"],
        "url": "https://example.com/os/processes-and-pipes"
    },
    {
        "title": "CPU Scheduling Algorithms: FCFS, SJF, and Round Robin Explained",
        "subject": "Operating Systems",
        "topic": "CPU Scheduling",
        "difficulty": "Beginner",
        "resource_type": "Video",
        "description": "Comprehensive tutorial explaining how the operating system scheduler allocates CPU execution time to ready processes using First-Come First-Served, Shortest Job First, and Round Robin scheduling.",
        "content": "CPU scheduling is the basis of multiprogrammed operating systems. By switching the CPU among processes, the OS makes the computer more productive. Key metrics include throughput, turnaround time, waiting time, and response time.",
        "tags": ["operating systems", "cpu scheduling", "round robin", "fcfs", "sjf"],
        "url": "https://example.com/os/cpu-scheduling"
    },
    {
        "title": "Deadlock Detection and Prevention: Banker's Algorithm",
        "subject": "Operating Systems",
        "topic": "Deadlocks & Synchronization",
        "difficulty": "Advanced",
        "resource_type": "Notes",
        "description": "In-depth computer science lecture notes analyzing the four necessary conditions for deadlock and proving system safety using Dijkstra's Banker's Algorithm.",
        "content": "A deadlock occurs when a set of processes are blocked because each process is holding a resource and waiting for another resource held by another process. Coffman conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.",
        "tags": ["operating systems", "deadlock", "bankers algorithm", "concurrency"],
        "url": "https://example.com/os/bankers-algorithm"
    },
    {
        "title": "Relational Database Normalization: 1NF to 3NF & BCNF",
        "subject": "DBMS",
        "topic": "Database Design & Normalization",
        "difficulty": "Intermediate",
        "resource_type": "Article",
        "description": "Learn how to decompose database tables to eliminate data redundancy, update anomalies, and functional dependencies up to 3rd Normal Form and Boyce-Codd Normal Form.",
        "content": "Database normalization minimizes redundancy in a relational database schema. 1NF removes repeating groups. 2NF removes partial functional dependencies. 3NF removes transitive dependencies.",
        "tags": ["dbms", "sql", "normalization", "3nf", "bcnf", "database design"],
        "url": "https://example.com/dbms/normalization-guide"
    },
    {
        "title": "Mastering SQL Joins: Inner, Left, Right, and Full Outer Joins",
        "subject": "DBMS",
        "topic": "SQL Querying",
        "difficulty": "Beginner",
        "resource_type": "Interactive",
        "description": "Visual interactive exercises demonstrating how SQL joins combine rows from two or more database tables based on related key columns.",
        "content": "SQL JOIN clauses merge columns from one or more tables. INNER JOIN returns matching keys in both tables. LEFT JOIN returns all rows from the left table and matched rows from the right table.",
        "tags": ["dbms", "sql", "joins", "inner join", "left join", "relational database"],
        "url": "https://example.com/dbms/sql-joins-interactive"
    },
    {
        "title": "ACID Properties and Transaction Management in Databases",
        "subject": "DBMS",
        "topic": "Transactions & Concurrency",
        "difficulty": "Intermediate",
        "resource_type": "Video",
        "description": "Detailed video explanation covering Atomicity, Consistency, Isolation, and Durability (ACID) guarantees in relational database engines and two-phase locking protocols.",
        "content": "A database transaction is a logical unit of work. Atomicity ensures all operations succeed or all roll back. Consistency maintains data invariants. Isolation prevents concurrent transaction interference. Durability guarantees committed changes persist.",
        "tags": ["dbms", "acid", "transactions", "concurrency", "locking"],
        "url": "https://example.com/dbms/acid-properties"
    },
    {
        "title": "Data Structures: Binary Search Trees (BST) and Balancing",
        "subject": "Data Structures",
        "topic": "Trees & Graph Algorithms",
        "difficulty": "Intermediate",
        "resource_type": "Article",
        "description": "Clear step-by-step guide explaining Binary Search Tree insertion, deletion, traversals (Inorder, Preorder, Postorder), and AVL self-balancing rotations.",
        "content": "A Binary Search Tree is a node-based binary tree data structure where left subtrees contain values smaller than the parent node and right subtrees contain values greater. Time complexity for search is O(log n) in balanced trees.",
        "tags": ["data structures", "bst", "binary tree", "avl tree", "algorithms"],
        "url": "https://example.com/dsa/bst-guide"
    },
    {
        "title": "Graph Algorithms: Dijkstra's Shortest Path Algorithm",
        "subject": "Data Structures",
        "topic": "Graphs & Pathfinding",
        "difficulty": "Advanced",
        "resource_type": "Notes",
        "description": "Algorithmic analysis and C++/Python code implementations of Dijkstra's algorithm for finding shortest paths in weighted non-negative graphs using Min-Heaps.",
        "content": "Dijkstra's algorithm finds the shortest path from a single source vertex to all other vertices in a weighted graph. Using a priority queue min-heap, Dijkstra runs in O((V + E) log V) time complexity.",
        "tags": ["dsa", "graphs", "dijkstra", "shortest path", "min heap"],
        "url": "https://example.com/dsa/dijkstra-algorithm"
    },
    {
        "title": "Arrays, Linked Lists, and Dynamic Memory Allocation",
        "subject": "Data Structures",
        "topic": "Linear Data Structures",
        "difficulty": "Beginner",
        "resource_type": "Book",
        "description": "Fundamental textbook chapter contrasting contiguous array memory allocation with pointer-based singly and doubly linked list structures.",
        "content": "Arrays provide O(1) random memory index access but fixed contiguous memory allocation. Linked lists consist of nodes containing data and pointers, enabling dynamic memory allocation with O(1) head insertion.",
        "tags": ["dsa", "arrays", "linked list", "memory", "pointers"],
        "url": "https://example.com/dsa/arrays-vs-linked-lists"
    },
    {
        "title": "Object-Oriented Programming (OOP) Principles in Java",
        "subject": "Java",
        "topic": "Core Java & OOP",
        "difficulty": "Beginner",
        "resource_type": "Article",
        "description": "Learn the four core pillars of Object-Oriented Programming in Java: Encapsulation, Inheritance, Polymorphism, and Abstraction with real-world code examples.",
        "content": "Encapsulation hides internal object state behind private fields and public getters/setters. Inheritance allows child classes to reuse parent code. Polymorphism enables method overriding and interface dynamic dispatch.",
        "tags": ["java", "oop", "polymorphism", "inheritance", "encapsulation"],
        "url": "https://example.com/java/oop-principles"
    },
    {
        "title": "Java Multithreading and Concurrency Utilities (java.util.concurrent)",
        "subject": "Java",
        "topic": "Concurrency & Multithreading",
        "difficulty": "Advanced",
        "resource_type": "Video",
        "description": "Advanced masterclass covering Java Thread lifecycles, synchronized blocks, volatile keywords, ExecutorServices, and ThreadPoolExecutors.",
        "content": "Multithreading in Java permits concurrent execution of two or more threads. Java Memory Model ensures visibility via volatile variables and mutual exclusion using reentrant locks and synchronized keywords.",
        "tags": ["java", "multithreading", "concurrency", "threadpool", "executor"],
        "url": "https://example.com/java/multithreading-masterclass"
    },
    {
        "title": "Python List Comprehesions, Generators, and Decorators",
        "subject": "Python",
        "topic": "Advanced Python Features",
        "difficulty": "Intermediate",
        "resource_type": "Article",
        "description": "Elevate your Python code quality using elegant list comprehensions, memory-efficient generator yields, and custom wrapper decorators.",
        "content": "List comprehensions offer a concise syntax to create lists based on existing iterables. Generators yield items one at a time using memory-efficient lazy evaluation. Decorators modify function behavior dynamically.",
        "tags": ["python", "generators", "decorators", "list comprehension", "clean code"],
        "url": "https://example.com/python/advanced-python-features"
    },
    {
        "title": "Introduction to Python Programming for Complete Beginners",
        "subject": "Python",
        "topic": "Python Basics",
        "difficulty": "Beginner",
        "resource_type": "Interactive",
        "description": "Hands-on interactive introduction to Python syntax, variables, conditional statements, loops, functions, and file handling.",
        "content": "Python is a high-level, interpreted programming language emphasizing readability with simple indentation syntax. Learn basic data types including strings, integers, floats, lists, and dictionaries.",
        "tags": ["python", "basics", "beginners", "syntax", "loops"],
        "url": "https://example.com/python/beginner-guide"
    },
    {
        "title": "TCP/IP vs OSI Model: Computer Networking Fundamentals",
        "subject": "Computer Networks",
        "topic": "Network Architecture & Protocols",
        "difficulty": "Beginner",
        "resource_type": "Notes",
        "description": "Structured comparison table and breakdown of the 7-layer OSI Model and 4-layer TCP/IP protocol suite (Application, Transport, Internet, Network Access).",
        "content": "The OSI model standardizes network communication functions across 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application. TCP provides reliable connection-oriented transport, while UDP is connectionless.",
        "tags": ["computer networks", "tcp ip", "osi model", "networking", "protocols"],
        "url": "https://example.com/networks/tcp-ip-osi-model"
    },
    {
        "title": "Introduction to Machine Learning: Supervised vs Unsupervised Learning",
        "subject": "Machine Learning",
        "topic": "ML Fundamentals",
        "difficulty": "Intermediate",
        "resource_type": "Article",
        "description": "Discover core Machine Learning paradigms including Supervised Classification/Regression, Unsupervised Clustering (K-Means), and Reinforcement Learning.",
        "content": "Supervised learning trains models on labeled datasets to map inputs to target outputs (e.g. Linear Regression, Decision Trees). Unsupervised learning discovers hidden patterns in unlabeled data using clustering.",
        "tags": ["machine learning", "ai", "supervised learning", "unsupervised learning", "k means"],
        "url": "https://example.com/ml/intro-supervised-unsupervised"
    }
]

def seed_database():
    """
    Connects to MongoDB Atlas, clears existing documents,
    computes 384-dim vector embeddings for each sample resource,
    and inserts them into the collection.
    """
    print("[SEED] Connecting to MongoDB Atlas...")
    col = get_db_connection()

    print("[SEED] Clearing existing documents in collection...")
    col.delete_many({})

    print(f"[SEED] Processing {len(SAMPLE_RESOURCES)} sample study resources...")
    documents_to_insert = []

    for idx, item in enumerate(SAMPLE_RESOURCES, start=1):
        title = item["title"]
        subject = item["subject"]
        topic = item["topic"]
        description = item["description"]
        content = item.get("content", "")

        text_for_embedding = f"{title}. {topic}. {description}. {content}"
        print(f"[{idx}/{len(SAMPLE_RESOURCES)}] Generating embedding for: '{title[:40]}...'")

        # Generate vector embedding
        embedding = generate_embedding(text_for_embedding)

        doc = {
            "title": title,
            "subject": subject,
            "topic": topic,
            "difficulty": item["difficulty"],
            "resource_type": item["resource_type"],
            "description": description,
            "content": content,
            "tags": item["tags"],
            "url": item["url"],
            "created_at": datetime.utcnow(),
            "embedding": embedding
        }
        documents_to_insert.append(doc)
        time.sleep(0.2)  # Avoid rate limiting external API

    print("[SEED] Inserting documents into MongoDB Atlas...")
    result = col.insert_many(documents_to_insert)
    print(f"[SUCCESS] Seeded {len(result.inserted_ids)} resources into MongoDB Atlas successfully!")

if __name__ == "__main__":
    seed_database()
