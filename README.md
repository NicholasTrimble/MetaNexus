![Project Banner](static/images/banner.png)


MetaNexus is a full-stack deck-building application designed to help Trading Card Game players search for cards, manage their inventory, and construct custom decks. I built this project using Django and Python because I wanted to create a data-driven platform that could handle the complexity of massive card databases while keeping the user experience smooth and responsive.

One of the main technical challenges I solved was handling the sheer volume of card data efficiently. Rather than relying on slow manual entry or constant external API calls during user sessions, I engineered a custom bulk ingestion script that pulls over 30,000 records from the Scryfall API and synchronizes them with my local database in minutes.

On the frontend, I focused on usability by implementing live AJAX searching and filtering. This allows users to sort through thousands of cards by color, rarity, or name instantly without the friction of constantly reloading the page. The app also features a full user authentication system, allowing individuals to securely save, edit, and delete their own deck creations.

Currently, the platform is fully optimized for Magic: The Gathering, but I designed the backend architecture to be flexible. I am actively planning the next phase of development, which will introduce dedicated sections and logic for Pokémon and Yu-Gi-Oh!, effectively turning this into a multi-game hub for collectors and players alike.



How to Run Locally

1.  Clone the repository:    git clone https://github.com/nicholastrimble/metanexus.git

2.  Install dependencies:   pip install -r requirements.txt

3.  Initialize the database:   python manage.py migrate

4.  Fetch card data:   python manage.py update_cards_bulk

5.  Start the server:   python manage.py runserver
