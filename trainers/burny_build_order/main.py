import os
import sys

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))
# Add the relative path for the bot script to sys.path
main_bot_path = os.path.abspath(os.path.join(dir_path, "..", "..", "sc2city"))
sys.path.append(main_bot_path)

from build_order_extractor import BuildOrderExtractor


url = "https://burnysc2.github.io/sc2-planner/?&race=terran&bo=002eJy9UssKwjAQ/Jc992Cy1tT+ingobZAgtCUmiIj/7q0R7I5tkF4zzOw8cnqS66jelwWFx2ippvvgr9bTq/iFqOOE3IKPbYjeLqDpHaBBkCesaYMb+iXHtqEoFAmBOb0DJC0SexfSUqyBB7yjIKkNIBmpQtyFcCqnCUb2IAjbYFhVJbSfXMbx4pvuQ4/nKVwhhwdRT7IgWkN5xBXXXpFSrtXJSlGqeZL0/q9w21S7Np0y33/n/AYyNOO0"


if __name__ == "__main__":
    bo_extractor = BuildOrderExtractor(url, dir_path)
    bo_extractor.get_build_order()
