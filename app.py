from engine.ui_layout import ui_layout
from database import db_handler

if __name__ == "__main__":
    # initialize connection
    db_handler.prepare_db_handler()
    
    # setup database
    db_handler.setup_database()

    # launch gui
    ui_layout.launch()
