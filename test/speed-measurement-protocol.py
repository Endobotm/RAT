import time

# client side
curr_time_unix = time.time()
chunk = "T" * 1024 * 1024
payload = str(chunk) + str(curr_time_unix)

# server side
data = payload
server_curr_time_unix = time.time()
client_sent_time = float(data[1024 * 1024 :])
latency = server_curr_time_unix - client_sent_time
print(latency)
