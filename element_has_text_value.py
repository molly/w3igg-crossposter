class element_has_text_value(object):
    """An expectation for checking that an element has a particular text value.

    locator - used to find the element
    returns the WebElement once it has the specified text value
    """

    def __init__(self, locator, text_value):
        self.locator = locator
        self.text_value = text_value

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if element.text == self.text_value:
            return element
        else:
            return False
