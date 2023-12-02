#coding=utf-8

import curses

import render


def main():
    curses.wrapper(render.init)


if __name__ == "__main__":

    main()



    