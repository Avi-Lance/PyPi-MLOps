import pandas as pd
import numpy as np
import sklearn
sklearn.set_config(transform_output="pandas")  #pass pandas tables through pipeline instead of numpy matrices
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

class CustomMappingTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, mapping_column, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.'
    self.mapping_dict = mapping_dict
    self.mapping_column = mapping_column

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.mapping_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column "{self.mapping_column}"'  #column legit?

    #Set up for producing warnings. First have to rework nan values to allow set operations to work.
    #In particular, the conversion of a column to a Series, e.g., X[self.mapping_column], transforms nan values in strange ways that screw up set differencing.
    #Strategy is to convert empty values to a string then the string back to np.nan
    placeholder = "NaN"
    column_values = X[self.mapping_column].fillna(placeholder).tolist()  #Convert all nan values to the string "NaN" in new list
    column_values = [np.nan if v == placeholder else v for v in column_values]  #Now convert back to np.nan
    keys_values = self.mapping_dict.keys()

    column_set = set(column_values)  #Without the conversion above, the set will fail to have np.nan values where they should be
    keys_set = set(keys_values)      #This will have np.nan values where they should be so no conversion necessary

    #Verify all keys are contained in column
    keys_not_found = keys_set - column_set
    if keys_not_found:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these mapping keys do not appear in the column: {keys_not_found}\n")

    #Verify if keys are absent
    keys_absent = column_set -  keys_set
    if keys_absent:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these values in the column do not contain corresponding mapping keys: {keys_absent}\n")

    #Actual mapping
    X_ = X.copy()
    X_[self.mapping_column].replace(self.mapping_dict, inplace=True)
    return X_

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result

#This class will rename one or more columns.
class CustomRenamingTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, rename_dict:dict):
    assert isinstance(rename_dict, dict), f'{self.__class__.__name__} constructor expected dictionary for rename_dict but got {type(rename_dict)} instead.'
    self.rename_dict = rename_dict

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    missing_columns = [key for key in self.rename_dict.keys() if key not in X.columns.to_list()]
    if missing_columns:
        raise AssertionError(f'{self.__class__.__name__}: cannot rename unknown columns: {missing_columns}')

    X_ = X.copy()
    X_.rename(columns=self.rename_dict, inplace=True)
    return X_

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result

#This class will perform a One Hot Encoding
class CustomOHETransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, dummy_na=False, drop_first=False):
    self.target_column = target_column
    self.dummy_na = dummy_na
    self.drop_first = drop_first

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column "{self.target_column}"'

    X_ = X.copy()
    X_return = pd.get_dummies(X_,
                              prefix=self.target_column,
                              prefix_sep='_',
                              columns=[f'{self.target_column}'],
                              dummy_na=self.dummy_na,
                              drop_first=self.drop_first
                              )
    return X_return

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result
