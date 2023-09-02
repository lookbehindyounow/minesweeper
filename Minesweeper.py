
# ---------------------------------------------------------------------------------------------------------------- #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  #
#                                                  ~MINESWEEPER~                                                   #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  #
# ---------------------------------------------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------------------------------------------- #
#                           Importing Libraries, Loading Icons & Window Initialisation
# ---------------------------------------------------------------------------------------------------------------- #

from tkinter import * # <-- GUI library
from random import randint # <-- placing mines
from time import time,sleep # <-- timer

def window():
    global root,size_changed,explosion_pic,flag_pic,mine_pic,flagged_mine_pic
    root=Tk() # window
    root.geometry("720x720+-6+0")
    size_changed=False # keeping track of if the window's been resized at any point

    explosion_pic=PhotoImage(master=root,width=16,height=17,file="explosion.png") # loading images
    flag_pic=PhotoImage(master=root,width=16,height=17,file="flag.png")
    mine_pic=PhotoImage(master=root,width=16,height=17,file="mine.png")
    flagged_mine_pic=PhotoImage(master=root,width=16,height=17,file="flagged_mine.png")

# ---------------------------------------------------------------------------------------------------------------- #
#                                                       Menu
# ---------------------------------------------------------------------------------------------------------------- #

def menu():
    global root,outer_screen,size_changed,game_over,name,rows,columns,mines
    game_over=True # this boolean is false while the actual game is in play
    try:
        outer_screen.destroy() # get rid of whatever was in window before putting something new in
    except NameError:
        window()
    except TclError:
        window()
    if size_changed:
        root.geometry("720x720+-6+0") # resising if necessary
        size_changed=False
    outer_screen=Canvas(root)
    Label(outer_screen).grid() # spacer
    prompt_1=Label(outer_screen,text="name:") # these are the text fields & buttons for the menu
    prompt_1.grid()
    input_1=Entry(outer_screen)
    input_1.insert(0,name)
    input_1.grid(row=1,column=1)
    prompt_2=Label(outer_screen,text="rows:")
    prompt_2.grid()
    input_2=Entry(outer_screen)
    input_2.insert(0,rows)
    input_2.grid(row=2,column=1)
    prompt_3=Label(outer_screen,text="columns:")
    prompt_3.grid()
    input_3=Entry(outer_screen)
    input_3.insert(0,columns)
    input_3.grid(row=3,column=1)
    prompt_4=Label(outer_screen,text="mines:")
    prompt_4.grid()
    input_4=Entry(outer_screen)
    input_4.insert(0,mines)
    input_4.grid(row=4,column=1)
    Label(outer_screen).grid() # spacer
    start_button=Button(outer_screen,text="Start",command=lambda:setup(input_1.get(),input_2.get(),
                                                                       input_3.get(),input_4.get()))
    start_button.grid()
    leaderboard_button=Button(outer_screen,text="Leaderboards",command=present)
    leaderboard_button.grid(row=6,column=1)
    outer_screen.pack()

# ---------------------------------------------------------------------------------------------------------------- #
#                                                    Game Setup
# ---------------------------------------------------------------------------------------------------------------- #

def setup(var_input_1="",var_input_2=10,var_input_3=10,var_input_4=10):
    global outer_screen,first_click,game_over,name,rows,columns,mines
    go_on=True # this boolean goes false if something's wrong with the inputs
    try: # input validation
        rows=int(var_input_2)
        columns=int(var_input_3)
        mines=int(var_input_4)
        if mines>=rows*columns:
            go_on=False
            message="There must be at least one free space on the grid."
        if rows>(root.winfo_screenheight()-150)//21 or columns>(root.winfo_screenwidth()-40)//20:
            go_on=False
            message_1="'rows' must be less than "+str((root.winfo_screenheight()-150)//21)
            message_2=" & 'columns' must be less than "+str((root.winfo_screenwidth()-40)//20)
            message_3=" because of your screenheight & screenwidth."
            message=message_1+message_2+message_3 # <--^^ this is all just to fit the code into a nice block size
        if rows<1 or columns<1 or mines<1:
            go_on=False
            message="'rows', 'columns' & 'mines' must all be greater than 0."
    except ValueError:
        go_on=False
        message="'rows', 'columns' & 'mines' must all be integers."
    name=var_input_1
    if len(name)>40:
        go_on=False
        message="'name' must be less than 40 characters"
    if go_on:
        first_click=True # this boolean exists because the mine grid is set after you click the first square to
        game_over=False  # ensure you don't die on your first click
        set_gui()
    else: # if the input validation isn't passed a message is shown & then it goes back to the menu
        go_on=False
        outer_screen.destroy()
        outer_screen=Canvas(root)
        Label(outer_screen).pack() # spacer
        Label(outer_screen,text=message).pack()
        Label(outer_screen).pack() # spacer
        Button(outer_screen,text="Okay",command=menu).pack()
        outer_screen.pack()

def set_gui():
    global outer_screen,field,buttons,reset,time_label,size_changed
    outer_screen.destroy()
    screen_width="720"
    screen_height="720"
    if rows>31: # variable window size depending on how many squares
        screen_height=str(21*rows+90)
        size_changed=True
    if columns>34:
        screen_width=str(20*columns+40)
        size_changed=True
    if size_changed:
        root.geometry(screen_width+"x"+screen_height+"+-6+0")
    outer_screen=Canvas(root)
    Label(outer_screen).pack() # spacer
    field=Canvas(outer_screen)
    buttons=[[None for column in range(columns)]for row in range(rows)]
    for row in range(rows): # filling an empty 2D list with all the buttons for all the squares
        for column in range(columns):
            buttons[row][column]=Label(field,text="",relief=RAISED,height=1,width=2)
            buttons[row][column].bind("<Button-1>",lambda event,row=row,column=column:clicked(event,row,column))
            buttons[row][column].bind("<Button-3>",
                                      lambda event,row=row,column=column:clicked(event,row,column))
            buttons[row][column].bind("<ButtonRelease-1>",
                                      lambda event,row=row,column=column:reveal(event,row,column))
            buttons[row][column].bind("<ButtonRelease-3>",lambda event,row=row,column=column:flag(event,row,column))
            buttons[row][column].grid(row=row,column=column)
    field.pack()
    Label(outer_screen).pack() # spacer
    reset=Button(outer_screen,text="Reset",command=menu)
    reset.pack()
    time_label=Label(outer_screen)
    time_label.pack()
    outer_screen.pack()

def set_grid(row,column): # this is where the placement of the mines is decided
    global grid
    grid=[["U" for i in range(columns)]for j in range(rows)] # <-- creates grid
    # U=Unclicked                                   }# Button
    # M=Mine                                        }
    # [nothing]=empty                               }# Clicked
    # [number from 1-8]=empty with adjacent mines   }
    # FM=Flagged Mine                               }# Flagged
    # FF=False Flag                                 }
    mine_counter=mines
    while mine_counter>0:
        random_row=randint(0,rows-1)
        random_column=randint(0,columns-1) # ↓ensures mines aren't double-placed or placed where you first click
        if grid[random_row][random_column]=="U" and (random_row!=row or random_column!=column):
            grid[random_row][random_column]="M"
            mine_counter-=1

# ---------------------------------------------------------------------------------------------------------------- #
#                                             Game Mechanic Fucntions
# ---------------------------------------------------------------------------------------------------------------- #
    
def update_timer():
    global timer_start,time_label,game_over
    if not game_over:
        time_label.config(text=str(round(time()-timer_start,0))[0:-2]+"s")
        wait=1000*round((timer_start-time())%1,3) # keeps the timer synched with actual time
        root.after(int(wait),lambda:update_timer()) # keeps the timer updating
        
def clicked(event,row,column): # purely cosmetic, buttons go down when you click em but don't reveal til you let go
    try:
        if grid[row][column] in ["U","M","FF","FM"] and not game_over: # only if unclicked & the game is still going
            buttons[row][column].config(relief=SUNKEN)
    except NameError:
        buttons[row][column].config(relief=SUNKEN)
    except IndexError:
        buttons[row][column].config(relief=SUNKEN)

def reveal(event,row,column):
    global game_over,first_click,timer_start,explosion_pic
    if not game_over:
        if first_click: # changes the detection boolean, calls the function to place the mines & starts the timer
            first_click=False
            set_grid(row,column)
            timer_start=time()
            update_timer()
        if grid[row][column]in["U","FF"]: # if there's no mine to to the revealing algorithm
            iterative_reveal(row,column)
        elif grid[row][column]in["M","FM"]: # if there's a mine game over
            game_over=True
            buttons[row][column].config(image=explosion_pic,width=16,height=17)
            grid[row][column]="*" # so it doesn't get shown as an unexploded mine in the game over mine reveal
            end(False)
        check()

def recursive_reveal(row,column): # old method of doing the reveal, not in use but still works as an alternate method
    grid[row][column]=""          # to iterative_reveal (below)
    adjacent_mines=0
    for vertical in range(3): # each iteration scans a row in the surrounding 3x3 square
        if(row==0 and vertical==0)or(row==rows-1 and vertical==2): # skip 1st row scan if we're at the top
            continue                                               # or last row scan if we're at the bottom
        for horizontal in range (3): # the next 3 lines are the same stuff but for columns
            if(column==0 and horizontal==0)or(column==columns-1 and horizontal==2):
                continue
            if grid[row+vertical-1][column+horizontal-1]in["M","FM"]: # adjacent mine counter
               adjacent_mines+=1
    if adjacent_mines>0:
        grid[row][column]=str(adjacent_mines) # update grid
    buttons[row][column].config(text=grid[row][column], # show on screen with coloured numbers
                                fg=["white","blue","green","red","magenta","maroon","#0db879",
                                    "grey","black"][adjacent_mines],font=("Helvetica",9,"bold"),
                                relief=FLAT,image="",width=2,height=1)
    if adjacent_mines==0: # with this method it's easier to do the adjacent scan twice because of the fact the
                          # recursion happens in this nested loop & we need to know if there are any adjacent mines
                          # before we even do anything here
        for vertical in range(3):
            if(row==0 and vertical==0)or(row==rows-1 and vertical==2):
                continue
            for horizontal in range (3):
                if(column==0 and horizontal==0)or(column==columns-1 and horizontal==2):
                    continue # ↓recalls itself for all scanned unclicked squares
                if grid[row+vertical-1][column+horizontal-1]=="U":
                    # root.update() # unhash these 2 lines to show the recursive reveal path
                    # sleep(0.01)
                    recursive_reveal(row+vertical-1,column+horizontal-1)

def iterative_reveal(row,column): # more memory efficient method I think? defo seems faster too
    to_do=[(row,column)] # effectively a stack of the squares that need revealed
    while True:
        location=min(to_do)      # prioritises to do list of squares to reveal from the top down to save memory
        to_do.remove(min(to_do)) # (without this it's a very perculiar search path)
        grid[location[0]][location[1]]=""
        adjacent_mines=0
        new_places=0
        for vertical in range(3): # each iteration scans a row in the surrounding 3x3 square
            if(location[0]==0 and vertical==0)or(location[0]==rows-1 and vertical==2):
                continue # ^skip 1st row scan if we're at the top or last row scan if we're at the bottom
            for horizontal in range (3): # the next 3 lines are the same stuff but for columns
                if(location[1]==0 and horizontal==0)or(location[1]==columns-1 and horizontal==2):
                    continue
                if grid[location[0]+vertical-1][location[1]+horizontal-1]in["M","FM"]: # adjacent mine counter
                    adjacent_mines+=1
                if grid[location[0]+vertical-1][location[1]+horizontal-1]=="U":        # nested conditions to fit
                    if (location[0]+vertical-1,location[1]+horizontal-1) not in to_do: # the rest of the code
                        # ^if an adjacent square is unclicked & not already on the to do list
                        to_do.append((location[0]+vertical-1,location[1]+horizontal-1)) # put it in the to do list
                        new_places+=1 # & count how many new items were just put in incase they need removed
        if adjacent_mines>0: # in the event that the current square is numbered & not blank
            for i in range(new_places): # remove the newly added squares from the to do list
                to_do.pop()
            grid[location[0]][location[1]]=str(adjacent_mines) # update grid
        buttons[location[0]][location[1]].config(text=grid[location[0]][location[1]],
                                                 fg=["white","blue","green","red","magenta","maroon","#0db879",
                                                     "grey","black"][adjacent_mines],font=("Helvetica",9,"bold"),
                                                 relief=FLAT,image="",width=2,height=1)
        # root.update() # unhash these 2 lines to show the iterative reveal path (kind of boring when it's top down)
        # sleep(0.01)
        if len(to_do)==0:
            break # finish when to do list empties

def flag(event,row,column): # puts a flag when you right click
    global grid,first_click,timer_start,field,flag_pic
    if not game_over:
        if first_click:
            first_click=False
            set_grid(row,column)
            timer_start=time()
            update_timer()
        if grid[row][column]=="M":
            grid[row][column]="FM"
            buttons[row][column].config(image=flag_pic,relief=RAISED,width=16,height=17)
        elif grid[row][column]=="U":
            grid[row][column]="FF"
            buttons[row][column].config(image=flag_pic,relief=RAISED,width=16,height=17)
        elif grid[row][column]=="FM":
            grid[row][column]="M"
            buttons[row][column].config(image="",relief=RAISED,width=2,height=1)
        elif grid[row][column]=="FF":
            grid[row][column]="U"
            buttons[row][column].config(image="",relief=RAISED,width=2,height=1)
        check()

def check(): # this is called after every square clicked & it checks if the game's finished
    global game_over,grid,player_time
    if not game_over:
        game_over_brute=True # there are 2 ways to win minesweeper, flag all the mines or clear all the empty spaces
        game_over_flag=True
        for row in grid:
            for column in row:
                if column in["FF","U"]: # any empty spaces left un-revealed & you can't brute-force win
                    game_over_brute=False
                if column in["FF","M"]: # any incorrect flags or mines that aren't flagged & you can't flag win
                    game_over_flag=False
                if not game_over_brute and not game_over_flag: # leave the loop after both winning conditions aren't
                    break                                      # met to save time
            if not game_over_brute and not game_over_flag:
                break
        if game_over_brute or game_over_flag: # stop the timer & end the game when you win
            player_time=round(time()-timer_start,3)
            game_over=True
            end(True)

# ---------------------------------------------------------------------------------------------------------------- #
#                                                    Game Over
# ---------------------------------------------------------------------------------------------------------------- #

def end(win):
    global player_time,mine_pic,flagged_mine_pic
    for row in range(len(grid)): # reveals where the mines were
        for column in range(len(grid[row])):
            if grid[row][column]=="M":
                buttons[row][column].config(image=mine_pic,width=16,height=17)
            if grid[row][column]=="FM":
                buttons[row][column].config(image=flagged_mine_pic,width=16,height=17)
    if win:
        time_label.config(text=("Player time: "+str(player_time)+"s")) # shows your time
        reset.config(text="Congratulations!") # this is what the reset button says when you win
        leaderboards=access() # get the leaderboards table from file
        if leaderboards is not None:
            player_mode_rank=[rows*columns,mines] # leaderboards are organised by rank - grid size & then mine count
            new_leaderboards=[]
            overwritten=False # this table is a list with sections & this boolean makes life easier
            for mode in leaderboards: # for each grid size & mine count combo
                mode_rank=[mode[0][0]*mode[0][1],mode[0][2]] # for comparison to our new time
                if player_mode_rank[0]>mode_rank[0]and not overwritten: # time is for a new grid size or previous
                    new_leaderboards.append([[rows,columns,mines],[(name,player_time)]]) # grid size with lowest
                    overwritten=True                                                     # mine count
                if player_mode_rank[0]==mode_rank[0]and not overwritten: # time is for the current grid size
                    if player_mode_rank[1]>mode_rank[1]: # time is for a new mine count
                        new_leaderboards.append([[rows,columns,mines],[(name,player_time)]])
                        overwritten=True
                    if player_mode_rank[1]==mode_rank[1]: # time is for the current minue count
                        new_mode=[]
                        for score in mode[1]: # for each time in rank
                            if player_time<score[1]and not overwritten:
                                new_mode.append((name,player_time)) # put time into new table section
                                overwritten=True
                            new_mode.append(score) # put existing times into new table section in order
                        if not overwritten:
                            new_mode.append((name,player_time)) # put time on at the end if it's the slowest
                            overwritten=True
                        mode[1]=new_mode # replace old table with new table for this rank
                new_leaderboards.append(mode) # write each section to new leaderboard table in order
            if not overwritten:
                new_leaderboards.append([[rows,columns,mines],[(name,player_time)]]) # time is for new lowest rank
            leaderboards=new_leaderboards # update leaderboards table
            
            file=open("leaderboard.txt","w") # overwrite leaderboards file with new table
            file.truncate()
            file_string=""
            for mode in leaderboards: # file formate is explained further in access()
                file_string+=str(mode[0][0])+","+str(mode[0][1])+","+str(mode[0][2])+":"
                for score in mode[1]:
                    file_string+=str(score[0])+","+str(score[1])+";"
                file_string=file_string[0:-1]+"\n"
            file.write(file_string)
            file.close()
        else:
            file=open("leaderboard.txt","w") # if there is no file then make one
            file.write(str(rows)+","+str(columns)+","+str(mines)+":"+name+","+str(player_time)+"\n")
            file.close()
    else:
        reset.config(text="Fucked it again") # this is what the reset button says when you lose

# ---------------------------------------------------------------------------------------------------------------- #
#                                                   Leaderboards
# ---------------------------------------------------------------------------------------------------------------- #

def mouse_scroll(event): # this is the event called by the mouse scrollwheel & where it links to the scrollable bit
    boardframe.yview_scroll(-int(event.delta/120),"units")

def present(): # shows the leaderboards
    global outer_screen,boardframe
    outer_screen.destroy()
    outer_screen=Canvas(root)
    Label(outer_screen).grid(row=0) # spacer
    leaderboards=access() # get the leaderboards table from file
    if leaderboards:
        Label(outer_screen,text="Player",relief=RIDGE,width=64).grid(row=1)
        Label(outer_screen,text="Time",relief=RIDGE,width=15).grid(row=1,column=1)
        Label(outer_screen).grid(row=2) # spacer

        boardframe=Canvas(outer_screen,yscrollincrement="20") # this is the object that is scrollable
        boardframe.bind_all("<MouseWheel>",mouse_scroll) # this is what calls the event when the mouse wheel scrolls
        boardframe.grid(row=3,columnspan=2)
        scrollbar=Scrollbar(outer_screen,command=boardframe.yview) # this is the scrollbar you can click & drag
        scrollbar.grid(row=3,column=2,sticky="ns")
        boardframe.config(yscrollcommand=scrollbar.set)
        
        board=Canvas(boardframe) # this is where the actual tables are put on screen
        lines=1
        for mode in leaderboards: # for every rank
            Label(board,text=str(mode[0][0])+"x"+str(mode[0][1])+" grid, "+str(mode[0][2])+" mines").grid()
            for entry in mode[1]: # for every time
                Label(board,text=entry[0],relief=RIDGE,width=64).grid()
                written_time=str(round(entry[1]%60,4))+"s" # this bit figures out if it goes into minutes or hours
                if entry[1]>=60:
                    written_time=str(int(entry[1]%3600//60))+"m "+written_time
                    if entry[1]>=3600:
                        written_time=str(int(entry[1]//3600))+"h "+written_time
                Label(board,text=written_time,relief=RIDGE,width=15).grid(row=lines,column=1)
                lines+=1
            if leaderboards.index(mode)!=len(leaderboards)-1:
                Label(board).grid() # spacer label for gaps between each board
            lines+=2
        
        boardframe.create_window((0,0),window=board,anchor="nw") # this is all more scrollbar stuff
        board.update_idletasks() # keeps the scrollbar updating
        boardframe.config(width=561,height=min(lines*21-42,538))
        boardframe.config(scrollregion=boardframe.bbox("all"))
        
        clear=Button(outer_screen,text="Clear leaderboards",command=empty_leaderboards,width=15)
        clear.grid(row=5,columnspan=2)
        Label(outer_screen).grid(row=6) # spacer
    else: # if the leaderboards are empty
        Label(outer_screen,text="There are no leaderboard entries yet.").grid(row=1)
    Label(outer_screen).grid(row=4) # spacer
    reset=Button(outer_screen,text="Back",command=menu)
    reset.grid(row=7,columnspan=2)
    outer_screen.pack()

def access(): # reads the file & puts it into the nested list (table with sections)
    leaderboards=[]
    try:
        file=open("leaderboard.txt")
        for i in file:
            i=i[0:-1] # turns each line into a string (character array)
            line=i.split(":") # splits the rank from the corresponding scores
            mode=line[0].split(",") # next 5 lines format rank into a list from a string
            temp_mode=[]
            for num in mode:
                temp_mode.append(int(num))
            mode=temp_mode
            scores=line[1].split(";") # splits the scores up
            temp_scores=[]
            for j in scores: # splits name from time
                temp_entry=j.split(",")
                entry=(temp_entry[0],float(temp_entry[1]))
                temp_scores.append(entry)
            scores=temp_scores
            leaderboards.append([mode,scores]) # adds the section to our table
        file.close()
    finally:
        return leaderboards # if there is no file or an empty file, returns []

def empty_leaderboards(): # clears the leaderboards
    file=open("leaderboard.txt","w")
    file.truncate()
    file.close()
    present()

# ---------------------------------------------------------------------------------------------------------------- #
#                                                    Run Script
# ---------------------------------------------------------------------------------------------------------------- #

name="" # auto-filled values for the main menu
rows=10
columns=10
mines=10
menu() # runs the menu
root.mainloop() # gets the gui going

# ---------------------------------------------------------------------------------------------------------------- #
