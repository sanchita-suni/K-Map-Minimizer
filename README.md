# K-Map Solver

This project is a web-based Karnaugh Map (K-Map) solver designed to assist students and engineers in digital logic design. It provides a user-friendly interface to minimize boolean functions and generate corresponding logic representations.

The application features a modern frontend built with React and a high-performance Python backend using the FastAPI framework.

## Key Features

*   **Variable Input Methods**: Supports boolean functions with 2 to 15 variables. Users can define functions using:
    *   Minterms
    *   Maxterms
    *   Boolean Expressions

*   **Advanced Minimization Algorithm**: Implements a highly optimized Quine-McCluskey algorithm. It leverages bit-slicing and a branch-and-bound strategy for efficient and exact minimization, even with a higher number of variables.

*   **Comprehensive Solution Output**: The tool provides a complete set of results, including:
    *   Minimal Sum of Products (SOP) expression.
    *   Minimal Product of Sums (POS) expression.
    *   Lists of all prime implicants, with essential prime implicants clearly identified.
    *   Full truth table for the function.

*   **Interactive K-Map Visualization**: A visual representation of the Karnaugh Map is displayed, with colored groupings that correspond to the terms in the minimized SOP expression.

*   **Verilog HDL Generation**: Automatically generates synthesizable Verilog code for the minimized logic function in multiple standard modeling styles:
    *   Behavioral
    *   Dataflow
    *   Gate-level
    *   A complete Verilog testbench is also created to verify the functionality of the generated module.

*   **Performance Metrics**: The backend reports detailed performance data for each minimization, offering insights into the efficiency of the algorithm.

## Technology Stack

*   **Backend**: Python, FastAPI
*   **Frontend**: React.js, Tailwind CSS, shadcn/ui
*   **Core Algorithm**: Optimized Bit-Slice Quine-McCluskey with Branch-and-Bound

## Getting Started

### Prerequisites

*   Node.js and npm (for the frontend)
*   Python 3.x and pip (for the backend)

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn server:app --reload
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm start
```

The application will be available at `http://localhost:3000`.
