exemplars = """
{system_start}{system_message}{system_end}
{user_start}{user_lead_message}There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?{user_end}
{assistant_start}
Grove workers planted 21 - 15 = 6 trees today.
The answer is 6.{assistant_end}
{user_start}{user_lead_message}If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?{user_end}
{assistant_start}
Once 2 more cars arrive at the parking lot, which initially has 3 cars, the total number of cars in the parking lot increases to 5.
The answer is 5.{assistant_end}
{user_start}{user_lead_message}Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?{user_end}
{assistant_start}
Leah and her sister initially had 32 + 42 = 74 chocolates. After eating 35 chocolates, there are 74 - 35 = 39 chocolates left in total.
The answer is 39.{assistant_end}
{user_start}{user_lead_message}Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?{user_end}
{assistant_start}
The difference between the number of lollipops Jason had initially and the number he has now will give us the number of lollipops he gave to Denny. So, we need to subtract the current number of lollipops (12) from the initial number (20).

Jason gave Denny (20 - 12) = 8 lollipops.
The answer is 8.{assistant_end}
{user_start}{user_lead_message}Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?{user_end}
{assistant_start}
Shawn initially has 5 toys. After receiving 2 toys from his mom and 2 toys from his dad, he has 5 (initial toys) + 2 (toys from mom) + 2 (toys from dad) = 9 toys.
The answer is 9.{assistant_end}
{user_start}{user_lead_message}There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?{user_end}
{assistant_start}
The addition of computers happened over four days, so we add the number of computers installed each day to the initial number. This gives us:

Number of computers = Initial number + (Computers installed on Monday + Computers installed on Tuesday + Computers installed on Wednesday + Computers installed on Thursday)
= 9 + (5 + 5 + 5 + 5)
= 9 + 20
= 29

So, there are now 29 computers in the server room.
The answer is 29.{assistant_end}
{user_start}{user_lead_message}Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?{user_end}
{assistant_start}
To answer the problem, we first need to account for the balls Michael lost on Tuesday, which leaves him with 58 - 23 = 35 balls. Then, we need to account for the balls he lost on Wednesday, which leaves him with 35 - 2 = 33 balls. Therefore, Michael had 33 golf balls remaining at the end of Wednesday.
The answer is 33.{assistant_end}
{user_start}{user_lead_message}Olivia has $23. She bought five bagels for $3 each. How much money does she have left?{user_end}
{assistant_start}
First, calculate the total cost of the bagels: 5 bagels * $3/bagel = $15.
Then, subtract this amount from Olivia's initial money to find out how much she has left: $23 - $15 = $8.
So, Olivia has $8 left after buying the bagels.
The answer is 8.{assistant_end}
{user_start}{user_lead_message}"""
