import os, sys
import re
import discord
import formatter as fmt
## v 1.2 (updated 20/05/2021)
class TestAuthUser:
     def __init__(self, ident):
          self.id = ident
          

class AuthorizedUsers:
     def __init__(self, lis):
          self.check_user = lambda exuserId: exuserId in lis
          self.get_rolesId = lambda roleList: [role.id for role in roleList]# input is Role objs
          self.check_roles = lambda roles: True in [True for roleId in self.get_rolesId(roles) if roleId in lis]
          

     
def get_auth_users(file="auth-users.txt"):
     file = open(file)
     lines = [line.strip() for line in file.readlines()]
     file.close()
     #print(auth_users)
     return AuthorizedUsers(
          [int(user) for user in lines if user.startswith("#") == False])

def check_auth(User, file="auth-users.txt"):
     return bool(get_auth_users(file).check_user(User.id))

def check_roles_for_moderator(User): # discord.Messageable
     #User = packet.author
     #guild = packet.guild ## FIX UP
     roles = User.roles
     #print(roles)
     return bool(get_auth_users("modroles.txt").check_roles(roles))
     

if __name__=="__main__":
     # 182481612028641280 = False
     testUser = TestAuthUser(182481612028641280)
     print(check_auth(testUser))
