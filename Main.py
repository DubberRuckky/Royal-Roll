import pymysql as sqlc
import random as rand
import customtkinter as ctk

gold=None
history = {}
#Connecting to the database
con=sqlc.connect(host = 'localhost',
                 user = 'root',
                 passwd = '*********')

csr=con.cursor()

csr.execute('create database if not exists royal_roll;')

csr.execute('use royal_roll;')

csr.execute('create table if not exists gold (gp INT);')

csr.execute('create table if not exists rolls (roll_id bigint primary key,dice_type varchar(10),roll int,total int);')

csr.execute('select count(*) from gold;')

if csr.fetchone()[0] == 0:
    csr.execute('insert into gold values(100);')
    con.commit()

def sql_casino_get():
    csr.execute('select * from gold')
    money=csr.fetchall()[0][0]
    return money

def sql_casino_write(value):
    csr.execute(f'update gold set gp={value};')
    con.commit()

def placeholder():
    print('Placeholder')

def casino():
    global gold
    gold=sql_casino_get()
    # --- UI Setup ---
    casino = ctk.CTk()
    casino.title("Casino")
    casino.geometry("480x700")

    gold_label = ctk.CTkLabel(casino, text=f"Gold: {gold}", font=("Arial", 16))
    gold_label.pack(pady=10)

    output = ctk.CTkTextbox(casino, height=220, width=400)
    output.pack(pady=10)
    output.insert(index="end", text="🎲 Welcome to Casino!\n")

    # --- Helper Functions ---
    def update_gold():
        sql_casino_write(gold)
        gold_label.configure(text=f"Gold: {gold}")

    def log(message):
        output.insert("end", message)
        output.see("end")

    # --- Game Logic ---
    def play(cost, max_reward, divisor=1):
        global gold
        if gold < cost:
            log("Not enough GP! Try watching an ad.\n")
            return

        gain = rand.randint(1, max_reward * divisor) // divisor
        gold += gain - cost
        update_gold()
        log(f"💰 You won {gain} GP (Cost {cost})\n")

    def ad():
        global gold

        gold += 10
        update_gold()
        log("📺 You watched an ad and gained +10 GP!\n")

    def tutorial():
        global gold
        log("\n📘 Tutorial Starting...\n")
        log("Step 1: Let's try Baby!\n")
        tut_gain = rand.randint(10, 15)
        gold += tut_gain - 10
        update_gold()
        log(f"🎉 You rolled Baby mode and won {tut_gain} GP!\n")
        log("Each mode costs GP and gives random rewards.\n")
        log("Higher levels = higher risks & rewards!\n")
        log("Use Ads to get more GP. Have fun!\n")

    def burn():
        global gold
        log("\n🔥 Burn Mode Started...\n")
        attempt = 1
        while gold >= 10:
            gain = rand.randint(1, 15)
            gold += gain - 10
            update_gold()
            log(f"Attempt {attempt}: Won {gain} GP\n")
            attempt += 1
        log(f"💀 Burnt out! Took {attempt - 1} attempts.\n")

    def casino_close():
        casino.destroy()
        ui()

    def baby():
        play(10, 15, 1)
    def easy():
        play(20, 35, 10)
    def medium():
        play(30, 55, 100)
    def hard():
        play(40, 75, 1000)
    def hellfire():
        play(50, 95, 10000)

    ctk.CTkButton(casino, text="Baby (10 GP)", command=baby).pack(pady=2)
    ctk.CTkButton(casino, text="Easy (20 GP)", command=easy).pack(pady=2)
    ctk.CTkButton(casino, text="Medium (30 GP)", command=medium).pack(pady=2)
    ctk.CTkButton(casino, text="Hard (40 GP)", command=hard).pack(pady=2)
    ctk.CTkButton(casino, text="Hellfire (50 GP)", command=hellfire).pack(pady=2)

    ctk.CTkLabel(casino,text=None).pack(pady=10)

    ctk.CTkButton(casino, text="📺 Watch Ad (+10 GP)", command=ad).pack(pady=2)
    ctk.CTkButton(casino, text="📘 Tutorial", command=tutorial).pack(pady=2)
    ctk.CTkButton(casino, text="🔥 Burn Mode", command=burn).pack(pady=2)
    ctk.CTkButton(casino, text="❌ Exit", command=casino_close).pack(pady=2)

    # --- Run ---
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    casino.mainloop()

# --- Dice Functions ---
def get_sql_dice():
    global history

    csr.execute('select * from rolls;')
    temp_dict = csr.fetchall()
    history.clear()

    for row in temp_dict:
        roll_id, dice_type, roll, total = row
        history[roll_id] = (dice_type, roll, total)


def write_sql_dice():
    global history

    csr.execute('truncate table rolls;')

    for k, v in history.items():
        dice_type, roll, total = v
        csr.execute('insert into rolls values(%s, %s, %s, %s);', (k, dice_type, roll, total))
    con.commit()


def dice():
    global history
    get_sql_dice()

    dice = ctk.CTk()
    dice.title("Dice Roller")
    dice.geometry("480x720")

    label = ctk.CTkLabel(dice, text="Select Dice and Roll", font=("Arial", 16))
    label.pack(pady=10)

    dice_var = ctk.StringVar(value="20")

    dice_options = ["2", "4", "6", "8", "10", "12", "20", "100", "Custom"]
    dropdown = ctk.CTkOptionMenu(dice, values=dice_options, variable=dice_var)
    dropdown.pack(pady=5)

    mod_label = ctk.CTkLabel(dice, text="Modifier:")
    mod_label.pack()

    mod_entry = ctk.CTkEntry(dice)
    mod_entry.pack(pady=5)

    output = ctk.CTkTextbox(dice, width=440, height=200)
    output.pack(pady=10)
    output.insert("end", "Welcome to Dice Roller!\n")

    def generate_unique_id():
        while True:
            roll_id = int(rand.random() * rand.random() * rand.random() * (10 ** 10))
            if roll_id not in history:
                return roll_id

    def roll_dice():
        try:
            temp_mod = mod_entry.get()
            if len(temp_mod) != 0:
                modifier = int(temp_mod)
            else:
                modifier = 0
        except ValueError:
            output.insert("end", "\nInvalid modifier! Must be an integer.\n")
            return

        sides = dice_var.get()
        if sides == "Custom":
            prompt_custom_die(modifier)
            return

        sides = int(sides)
        roll = rand.randint(1, sides)
        total = roll + modifier

        message = f"\nRolled a d{sides}: {roll} + {modifier} = {total}"
        if sides == 20 and roll == 20:
            message += " 🎉 NAT 20!"

        roll_id = generate_unique_id()
        history[roll_id] = (f"d{sides}", roll, total)
        write_sql_dice()
        output.insert("end", f"{message}\nYour Roll ID: {roll_id}\n")

    def prompt_custom_die(modifier):
        popup = ctk.CTkInputDialog(text="Enter number of sides for your custom die:", title="Custom Die")
        result = popup.get_input()
        try:
            sides = int(result)
            if sides < 2:
                raise ValueError
        except ValueError:
            output.insert("end", "\nInvalid number of sides.\n")
            return

        roll = rand.randint(1, sides)
        total = roll + modifier
        roll_id = generate_unique_id()
        history[roll_id] = (f"d{sides}", roll, total)
        write_sql_dice()
        output.insert("end", f"\nRolled a d{sides}: {roll} + {modifier} = {total}\nRoll ID: {roll_id}\n")

    def show_history():
        output.insert("end", "\n--- Roll History ---\n")
        for k, v in history.items():
            output.insert("end", f"ID {k}: {v}\n")
        output.insert("end", "--- End of History ---\n")

    def dice_close():
        dice.destroy()
        ui()

    ctk.CTkButton(dice, text="Roll Dice", command=roll_dice).pack(pady=10)

    ctk.CTkButton(dice, text="Show Roll History", command=show_history).pack(pady=5)

    ctk.CTkButton(dice, text="Exit", command=dice_close).pack(pady=15)

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    dice.mainloop()

#This is the function for the main UI and is the first thing the user sees
def ui():
    #This creates the app frame
    app = ctk.CTk()
    app.geometry('480x720')
    app.title("Royal Roll")

    def close_ui():
        app.destroy()

    def open_casino():
        close_ui()
        casino()

    def open_dice():
        close_ui()
        dice()

    welcome = ctk.CTkLabel(app, font=(None, 30), text='Welcome to\n\nRoyal Roll\nCasino Simulator and Dice Roller', text_color='#40E0D0')
    welcome.pack(pady=30)

    frame_buttons = ctk.CTkFrame(app)
    frame_buttons.pack(padx=40,pady=40,fill='both')

    casio_button=ctk.CTkButton(frame_buttons,text='Casino',command=open_casino)
    casio_button.pack(padx=40, pady=40)

    dice_button=ctk.CTkButton(frame_buttons,text="Dice Roller",command=open_dice)
    dice_button.pack(padx=40,pady=40)

    exit_button=ctk.CTkButton(app, text='Exit',command=close_ui)
    exit_button.pack(padx=40,pady=40)

    credits_name=ctk.CTkLabel(app,text="Project by Dubber Ruckky\n\nhttps://github.com/DubberRuckky/Royal-Roll")
    credits_name.pack(side='bottom',padx=20,pady=20)

    app.mainloop()

if __name__=='__main__':
    ui()
