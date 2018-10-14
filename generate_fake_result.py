import pandas as pd

def format_review(col,ifnan_col):
  new_col =[]
  for n in range(len(ifnan_col)):
    if ifnan_col[n] == 1:
      string = col[n].replace(",", "")
      lst = string.split(' ')
      new_col.append((float)(lst[0]))
    else:
      new_col.append(col[n])
  return new_col


def convert_reviews_toFloat():
    does_review_exist = data_df['Reviews'].notnull().astype(int)
    data_df['Reviews'] = format_review(data_df['Reviews'], does_review_exist)



def calc_sec_arrive(reviews, price):
    if(price == 0):
        price = 2*60
    else:
        price = 1*60 * price
    return (0.6 * reviews) + price


FILE_NAME = 'Data/raw_data.csv'
READY_SEC = 45 * 60
DRIV_PER = 2*60*60
BREAK_TIME = 30*60

data_df = pd.read_csv(FILE_NAME)
drive_lst = []

convert_reviews_toFloat()
review_col = data_df['Reviews'].fillna(0)
price_level_col = data_df['Price Level'].fillna(0)

for n in range(len(data_df)):
    dri_dur = data_df['Driving_Duration'][n]
    min_arrive_early = calc_sec_arrive(review_col[n], price_level_col[n])
    if dri_dur > DRIV_PER:
        period = dri_dur / DRIV_PER
        dri_dur = dri_dur + (period*BREAK_TIME)

    dri_dur = dri_dur + READY_SEC + min_arrive_early
    drive_lst.append(dri_dur)


data_df['Total_Driving'] = drive_lst

data_df.to_csv('Data/converted_data_with_totalDuration2.csv', index=False)


