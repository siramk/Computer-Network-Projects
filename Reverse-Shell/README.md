run "python server.py" on one terminal and "python client.py" on one or more other terminals.

on server.py execution, there will be a "COMM>" promt available to us. 
On entering "help", it will produce the list of commands available.

there are 4 options available.those are:
1.) list- prints all online connections
2.) select - select <client_id> selects a client with client_id and allows to send commands
3.) quit - quits current connection with the client you are talking to(to be used when in select mode)
4.) shutdown - shutsdown the server
NOTE: please use select command only after using list command(beacuse 'list' will remove any stale connectionsin 'self.connections' variable and display only active ones).
after using select command, you can start executing unix/linux commands along with "getfile" and "sendfile" commands which are created by me.

Further details can be found in screen shots of q1 in report.

press Ctrl + C in both server and client terminals to stop execution.
