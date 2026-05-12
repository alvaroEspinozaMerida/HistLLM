import util
def create_sample_data():
    engine = util.get_engine()

    bio_dataset = util.load_table_as_dataset(
        engine=engine,
        table_name="biographies",
        columns=["curid", "name", "biography"],
    )
    selected_figures = [
        "Julius Caesar",
        "Augustus",
        "Alexander the Great",
        "Cleopatra",
        "Socrates",
        "Plato",
        "Aristotle",
        "Confucius",
        "Qin Shi Huang",
        "Hannibal",
        "Constantine the Great",
        "Charlemagne",
        "William the Conqueror",
        "Saladin",
        "Genghis Khan",
        "Marco Polo",
        "Joan of Arc",
        "Christopher Columbus",
        "Leonardo da Vinci",
        "Michelangelo",
        "Nicolaus Copernicus",
        "Galileo Galilei",
        "Johannes Kepler",
        "Isaac Newton",
        "Voltaire",
        "George Washington",
        "Thomas Jefferson",
        "Napoleon",
        "Simón Bolívar",
        "Abraham Lincoln",
        "Charles Darwin",
        "Nikola Tesla",
        "Marie Curie",
        "Sigmund Freud",
        "Mahatma Gandhi",
        "Winston Churchill",
        "Franklin D. Roosevelt",
        "Joseph Stalin",
        "Adolf Hitler",
        "Nelson Mandela",
        "Martin Luther King Jr.",
        "Albert Einstein",
        "Alan Turing",
        "Ada Lovelace",
        "Malcolm X",
        "Che Guevara",
        "Mao Zedong",
        "Ho Chi Minh",
        "John F. Kennedy",
        "Margaret Thatcher"
    ]
    selected_df = bio_dataset.to_pandas()

    selected_df = selected_df[
        selected_df["name"].isin(selected_figures)
    ]

    selected_df = selected_df[
        ["curid", "name", "biography"]
    ]

    print(selected_df.head())
    print(selected_df.shape)
    selected_df.to_csv(
        "historical_figures_sample_og.csv",
        index=False
    )