from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime
# {
#     chatid : {
#         users : {
#             username : {
#                 wallet : 10,
#                 bankbalance : 100,
#                 inventory : {
#                     item 1 : (quantity, price),
#                     item 2 : (quantity, price)
#                 },
#                 "last_beg" : datetime.datetime(2019, 3, 13, 8, 33, 36, 261052),
#                 "last_daily" : datetime.datetime(2019, 3, 13, 8, 33, 36, 261052),
#                 "last_search" : datetime.datetime(2019, 3, 13, 8, 33, 36, 261052)
#             }
#         },
#         shop : {
#             item 1 : (quantity, price),
#             item 2 : (quantity, price)
#         },
#         lottery : [username1,username2]
#     }
# }


# todo ============
# gambling
# challenge - two users


# item : (quantity, price)
shop_template = {
    "chips" : (15,10),
    "coke" : (10,25),
    "cake" : (5,100),
    "laptop" : (5, 1000),
}


# save monopoly data
def save_mono():
    f = open('data/monopoly','w')
    f.write(str(mono))
    f.close()

# load monopoly data
def load_mono():
    f = open('data/monopoly','r')
    data=f.read()
    f.close()
    return eval(data)


# initially load monopoly data
mono = load_mono()

# creating a new user if one doesnt exist
def user_init(chat_id, username):
    mono[chat_id]["users"][username] = {
        "wallet" : 0,
        "bankbalance" : 0,
        "inventory" : {}
    }
    

# initialize mono in a group chat
def mono_init(chat_id, username):
    mono[chat_id] = {
        "users" : {},
        'shop': shop_template,
        "lottery" : []
    }
    user_init(chat_id, username)
    save_mono()
    



def check_mono_initialized(chat_id,username):
    if not chat_id in mono:
        mono_init(chat_id, username)
    else:
        if not username in mono[chat_id]["users"]:
            user_init(chat_id, username)


def mono_handler(bot, update, msg_list):
    chat_id = update.message.chat_id
    username = update.message.from_user.username.lower()
    
    # Check if the monopoly has been initialised. (the chat_id and/or the username)
    check_mono_initialized(chat_id, username)

    user = mono[chat_id]["users"][username]

    # pls balance
    # pls deposit 100
    # pls withdraw 500
    # View the balance for User
    if msg_list[1] in ["balance"]:
        if len(msg_list) > 2: username = msg_list[2].replace("@","") 
        user = mono[chat_id]["users"][username]
        wallet = user['wallet']
        bankbalance = user["bankbalance"]
        update.message.reply_text("Balance Information: \n Wallet: "+ str(wallet) + "\n Bank: " + str(bankbalance) )



    # pls deposit all
    # pls deposit 200
    elif msg_list[1] in ["deposit"]:
        if len(msg_list) == 2 or msg_list[2] == "all":
            user["bankbalance"] += user["wallet"]
            user["wallet"] = 0
            update.message.reply_text("All your money is deposited.")
        else:
            money = int(msg_list[2])
            if money <= user["wallet"]:
                user["bankbalance"] += money
                user["wallet"] -= money
                update.message.reply_text(str(money) + " has been deposited.")
            else:
                update.message.reply_text("You dont have that kind of money in your wallet.")
        


    # pls withdraw all
    # pls withdraw 200
    elif msg_list[1] in ["withdraw"]:
        if len(msg_list) == 2 or msg_list[2] == "all":
            user["wallet"] += user["bankbalance"]
            user["bankbalance"] = 0 
            update.message.reply_text("All your money is withdrawn.")
        else:
            try:
                money = int(msg_list[2])
            except:
                update.message.reply_text("Please Enter a numeric value or all.")
                return
            if money <= user["bankbalance"]:
                user["wallet"] += money
                user["bankbalance"] -= money
                update.message.reply_text(str(money) + " has been withdrawn.")
            else:
                update.message.reply_text("You dont have that kind of money in your bank.")



    # pls shop
    elif msg_list[1] in ["shop","market", "store"]:
        shop = mono[chat_id]["shop"]
        items_str = "Shop Items :\n--------------\n"
        for key in shop:
            q,p = shop[key]
            items_str += key + "  ("+ str(q) +") = Rs" + str(p) + "\n"
        update.message.reply_text(items_str)
    


    # pls buy coke
    # Buy items at store
    elif msg_list[1] in ["buy", "purchase"]:
        shop= mono[chat_id]["shop"]
        shop_item = msg_list[2]
        quantity, price = shop[shop_item]
        if quantity > 0:
            if price > user["wallet"]:
                update.message.reply_text("You broke af.")
                return
            shop[shop_item] = quantity - 1, price
            user["wallet"] -= price
            if shop_item in user["inventory"]:
                q,p = user["inventory"][shop_item]
                user["inventory"][shop_item] = q+1,p
            else:
                user["inventory"][shop_item] = (1,price)
            update.message.reply_text("Item " + shop_item + " has been purchased")
        else:   # quantity == 0
            update.message.reply_text("Item is out of stock.")

    
    # pls sell coke
    elif msg_list[1] in ["sell"]:
        shop = mono[chat_id]["shop"]
        shop_item = msg_list[2]
        if not shop_item in user["inventory"]:
            update.message.reply_text("You dont have that item.")
            return
        q, p = user["inventory"][shop_item]
        user["wallet"] += p 
        quantity, price = shop[shop_item]
        shop[shop_item] = quantity + 1, price
        if q==1 :
            user["inventory"].pop(shop_item)
        else:
            user["inventory"][shop_item] = q - 1,p 
        update.message.reply_text("Item has been sold")
        


    # pls inventory
    # View the Items in the Shop
    elif msg_list[1] in ["inventory"]:
        inventory = user["inventory"]
        items_str = "Inventory Items :\n"
        for key in inventory:
            q,p = inventory[key]
            items_str += key + "  ("+ str(q) +") = Rs" + str(p) + "\n"
        update.message.reply_text(items_str)
    
    

        

    # pls lottery results
    # pls lottery buy
    # pls lottery view 
    elif msg_list[1] in ["lottery"]:
        lottery_users = mono[chat_id]["lottery"]
        if msg_list[2] in ["buy"]:
            if username in lottery_users:   # participated already
                update.message.reply_text("You have already participated. Use \npls lottery results")
            else:   # participate in lottery
                if mono[chat_id]["users"][username]["wallet"] >= 10:
                    mono[chat_id]["users"][username]["wallet"] -= 10
                    lottery_users.append(username)
                    update.message.reply_text("You have successfully participated in the lottery.")
                else:
                    update.message.reply_text("You dont even have enough money to buy a lottery ticket.")
                
        elif msg_list[2] in ["view"]:
            update.message.reply_text("Lottery Participants :\n" + "\n".join(lottery_users))
        elif msg_list[2] in ["result","results"]:
            
            num = len(lottery_users)
            money = 10 * num * num
            import random 
            n = random.randint(0,len(lottery_users)-1)
            winner = lottery_users[n] # random select
            user = mono[chat_id]["users"][winner]
            user["wallet"] += money
            mono[chat_id]["lottery"] = []
            
            update.message.reply_text(winner + " won the lottery. Prize money : " + str(money))



    # pls gamble all
    # pls gamble 50
    elif msg_list[1] in ["gamble"]:
        # check wallet status
        if msg_list[2] == "all":
            money = user["wallet"]
            if money < 2:
                update.message.reply_text("You dont have enough money to gamble.")
                return
            user["wallet"] = 0
        else:
            money = int(msg_list[2])
            if money < 2 or money > user["wallet"]:
                update.message.reply_text("You dont have enough money to gamble.")
                return
            user["wallet"] -= money

        import random
        game = random.randint(1,2)
        multiplier =  float(random.randint(80,100) /100)

        if game==2:  # win
            money += int(money * multiplier)
            user["wallet"] += int(money)
            update.message.reply_text("Congrats!!\nYou won this round. You got " + str(money))
        else: # lose
            update.message.reply_text("You lost this round.")



    # pls share @username 100
    # pls send @username 100
    elif msg_list[1] in ["share","send"]:
        if len(msg_list) == 2:
            update.message.reply_text("Please specify the user and amount, see \npls help share")
            return
        to_user = msg_list[2].replace("@","")
        money = int(msg_list[3])
        if user["wallet"] > money and money > 0:
            user["wallet"] -= money
            mono[chat_id]["users"][to_user]["wallet"] += money
            update.message.reply_text("Money has been sent.")
        else:
            update.message.reply_text("You dont have so much money to share.")



    # pls steal @username
    # need minumum 200
    elif msg_list[1] in ["steal"]:
        steal_from = msg_list[2].replace("@","")
        # check minimum 200 in either wallets
        money = mono[chat_id]["users"][steal_from]["wallet"]
        if money <= 200 or user["wallet"] <= 200:
            update.message.reply_text("Both you and the victim should have minimun 200 in the wallet to steal.")
            return
        # success or got caught
        import random
        steal_or_not = random.randint(1,2)

        if steal_or_not == 2: # steal successfull
            how_much = random.randint(1,int(money/2))
            mono[chat_id]["users"][steal_from]["wallet"] -= how_much
            user["wallet"] += how_much
            update.message.reply_text("You were able to steal " + str(how_much) + " from " + steal_from)

        else: # caught
            how_much = random.randint(1,int(user["wallet"]/2))
            user["wallet"] -= how_much
            mono[chat_id]["users"][steal_from]["wallet"] += how_much
            update.message.reply_text("Damn! You got caught and paid " + str(how_much) + " to " + steal_from)



    # pls beg
    # beg timer = 10s
    elif msg_list[1] in ["beg"]:
        import random
        if "last_beg" in user:
            if not (datetime.datetime.today() - user["last_beg"]).seconds > 10:
                update.message.reply_text("You're begging too much. Stop it!! (wait %d seconds)" % \
                                    (10-int((datetime.datetime.today() - user["last_beg"]).seconds)))
                return
        donators = ["Liam", "Noah", "William", "James", "Logan", "Benjamin", "Mason", "Elijah", "Oliver", "Jacob", "Lucas", "Michael", "Alexander", "Ethan", "Daniel", "Matthew", "Aiden", "Henry", "Joseph", "Jackson", "Samuel", "Sebastian", "David", "Carter", "Wyatt", "Jayden", "John", "Owen", "Dylan", "Luke", "Gabriel", "Anthony", "Isaac", "Grayson", "Jack", "Julian", "Levi", "Christopher", "Joshua", "Andrew", "Lincoln", "Mateo", "Ryan", "Jaxon", "Nathan", "Aaron", "Isaiah", "Thomas", "Charles", "Caleb", "Josiah", "Christian", "Hunter", "Eli", "Jonathan", "Connor", "Landon", "Adrian", "Asher", "Cameron", "Leo", "Theodore", "Jeremiah", "Hudson", "Robert", "Easton", "Nolan", "Nicholas", "Ezra", "Colton", "Angel", "Brayden", "Jordan", "Dominic", "Austin", "Ian", "Adam", "Elias", "Jaxson", "Greyson", "Jose", "Ezekiel", "Carson", "Evan", "Maverick", "Bryson", "Jace", "Cooper", "Xavier", "Parker", "Roman", "Jason", "Santiago", "Chase", "Sawyer", "Gavin", "Leonardo", "Kayden", "Ayden", "Jameson", "Kevin", "Bentley", "Zachary", "Everett", "Axel", "Tyler", "Micah", "Vincent", "Weston", "Miles", "Wesley", "Nathaniel", "Harrison", "Brandon", "Cole", "Declan", "Luis", "Braxton", "Damian", "Silas", "Tristan", "Ryder", "Bennett", "George", "Emmett", "Justin", "Kai", "Max", "Diego", "Luca", "Ryker", "Carlos", "Maxwell", "Kingston", "Ivan", "Maddox", "Juan", "Ashton", "Jayce", "Rowan", "Kaiden", "Giovanni", "Eric", "Jesus", "Calvin", "Abel", "King", "Camden", "Amir", "Blake", "Alex", "Brody", "Malachi", "Emmanuel", "Jonah", "Beau", "Jude", "Antonio", "Alan", "Elliott", "Elliot", "Waylon", "Xander", "Timothy", "Victor", "Bryce", "Finn", "Brantley", "Edward", "Abraham", "Patrick", "Grant", "Karter", "Hayden", "Richard", "Miguel", "Joel", "Gael", "Tucker", "Rhett", "Avery", "Steven", "Graham", "Kaleb", "Jasper", "Jesse", "Matteo", "Dean", "Zayden", "Preston", "August", "Oscar", "Jeremy", "Alejandro", "Marcus", "Dawson", "Lorenzo", "Messiah", "Zion", "Maximus"]
        beg_lines = ["go buy some food", "go gamble it", "go smoke some weed", "go eat some muffins", "go cry in the corner", "go buy some clothes", "go spend it wisely", "go get a life"]
        
        beg_from = donators[random.randint(0,len(donators)-1)]
        beg_line = beg_lines[random.randint(0,len(beg_lines)-1)]
        
        beg_amount = random.randint(10,60)
        user["wallet"] += beg_amount
        user["last_beg"] = datetime.datetime.today()
        update.message.reply_text(beg_from + " donated " + str(beg_amount) + " " + beg_line)


    # pls daily
    # daily timer = 1 day
    elif msg_list[1] in ["daily"]:
        if "last_daily" in user:
            diff_time = (datetime.datetime.today() - user["last_daily"])
            if diff_time.days < 1:
                diff_time = datetime.timedelta(days=1) - diff_time
                time_left = str(diff_time.seconds//3600) + "hrs and " + str((diff_time.seconds//60)%60) + "mins"
                update.message.reply_text("You have already gotten your share for the day, try again after " + time_left)
                return
        import random
        money = random.randint(200,300)
        user["wallet"] += money
        user["last_daily"] = datetime.datetime.today()
        update.message.reply_text("You got %d for the day, spend it wisely." % money)
        

    # pls search
    # search timer = 10s
    elif msg_list[1] in ["search"]:
        if "last_search" in user:
            if (datetime.datetime.today() - user["last_search"]).seconds < 10:
                update.message.reply_text("You need to wait "+ str(10-(datetime.datetime.today() - user["last_search"]).seconds) +"s to continue searching.")
                return
        import random
        money = random.randint(20,100)
        user["wallet"] += money
        user["last_search"] = datetime.datetime.today()
        search_strings = ["under the sofa", "inside the hidden pocket", "inside the kitchen box", "inside the safe", "inside the boot of your vehicle", "inside the lunchbox", "behind your phone car", "inside your girlfriend's bag", "inside the flush tank", "inside your bong pot", "inside a random person's buttcrack", "inside the dimensions of space", "inside the Washing machine lint drawer", "inside your cat's litter box"]
        search_string = search_strings[random.randint(0,len(search_strings)-1)]
        update.message.reply_text("Congrats you found " + str(money) + " " + search_string)



    # pls rich
    # list top 3 rich people
    elif msg_list[1] in ["rich"]:
        users = dict(mono[chat_id]["users"])
        max_list = []
        for i in range(3):
            max_wallet = -1
            max_user = None
            for u in users:
                if users[u]["wallet"] > max_wallet:
                    max_wallet = users[u]["wallet"]
                    max_user = u 
            max_list.append((max_user,max_wallet))
            try: 
                users.pop(max_user)
            except:
                break
        riches = "Rich People : \n"
        for item in max_list:
            u,w = item
            if u != None:
                riches += u + "  ("+ str(w) +")\n"
        update.message.reply_text(riches)



    # Finally save the monopoly data
    save_mono()