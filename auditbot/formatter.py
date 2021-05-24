

import os, sys
import discord
import re


class RolesList:
    def __init__(self, roleList):
        self.roleList = roleList # list of discord.Role objs
        self.roleNameList = [role.name for role in self.roleList]
        self.roleIdList = [role.id for role in self.roleList]

    def update(self, roleList):
        self.roleList = roleList
        self.roleNameList = [role.name for role in self.roleList]
        self.roleIdList = [role.id for role in self.roleList]
        return True
