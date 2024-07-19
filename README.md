# Raspagem

---

## Installation Guide

Follow these steps to set up and run the job scraping script.

### Prerequisites

Ensure you have the following installed on your system:
- Python 3.9
- pip (Python package installer)

### Step-by-Step Instructions

1. **Clone the Repository**

   Clone the repository to your local machine using the following command:

   ```bash
   git clone https://github.com/Projeto-Estagio/API-1-Raspagem.git
   ```

2. **Navigate to the Project Directory**

   Change to the project directory:

   ```bash
   cd API-1-Raspagem
   ```

3. **Install Dependencies**

   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the root directory of the project and add your Supabase URL and API key. The `.env` file should look like this:

   ```plaintext
   SUPABASE_URL=https://your-supabase-url
   SUPABASE_KEY=your-supabase-key
   ```

   Replace `https://your-supabase-url` and `your-supabase-key` with your actual Supabase URL and API key.

5. **Run the Script**

   You can now run the scraping script:

   ```bash
   python main.py
   ```

### Example

Here's an example of how to run the entire setup:

```bash
# Clone the repository
git clone https://github.com/Projeto-Estagio/API-1-Raspagem.git

# Navigate to the project directory
cd API-1-Raspagem

# Install dependencies
pip install -r requirements.txt

# Create .env file and add Supabase credentials
echo -e "SUPABASE_URL=https://your-supabase-url\nSUPABASE_KEY=your-supabase-key" > .env

# Run the script
python main.py
```

### Setting Up a Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies and avoid conflicts. Follow these steps to set up a virtual environment:

1. **Create a Virtual Environment**

   Create a virtual environment with:

   ```bash
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment**

   Activate the virtual environment with:

   ```bash
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies in the Virtual Environment**

   Install the required packages inside the virtual environment:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Script**

   Run the script as usual:

   ```bash
   python your_script.py
   ```

### Additional Notes

- Ensure your Python version is 3.9 to avoid compatibility issues.
- If you encounter any issues, please check the dependencies in `requirements.txt` and make sure they are installed correctly.

---