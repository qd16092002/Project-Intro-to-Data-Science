from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField,SelectMultipleField, widgets

class InputForm(FlaskForm):
    choices_estate_type = [
        ('Biệt thự', 'Biệt thự'),
        ('Biệt thự liền kề', 'Biệt thự liền kề'),
        ('Chung cư', 'Chung cư'),
        ('Các loại khác', 'Các loại khác'),
        ('Kho xưởng', 'Kho xưởng'),
        ('Mặt bằng', 'Mặt bằng'),
        ('Mặt bằng, cửa hàng', 'Mặt bằng, cửa hàng'),
        ('Nhà hàng, khách sạn', 'Nhà hàng, khách sạn'),
        ('Nhà mặt tiền', 'Nhà mặt tiền'),
        ('Nhà ngõ, hẻm', 'Nhà ngõ, hẻm'),
        ('Nhà phố', 'Nhà phố'),
        ('Nhà riêng', 'Nhà riêng'),
        ('Nhà xưởng', 'Nhà xưởng'),
        ('Nhà đất', 'Nhà đất'),
        ('Phòng trọ, nhà trọ', 'Phòng trọ, nhà trọ'),
        ('Shop, kiot, quán', 'Shop, kiot, quán'),
        ('Trang trại', 'Trang trại'),
        ('Trang trại khu nghỉ dưỡng', 'Trang trại khu nghỉ dưỡng'),
        ('Văn phòng', 'Văn phòng'),
        ('Đất', 'Đất'),
        ('Đất nông, lâm nghiệp', 'Đất nông, lâm nghiệp'),
        ('Đất nền dự án', 'Đất nền dự án'),
        ('Đất nền, phân lô', 'Đất nền, phân lô')
    
    ]
    estate_type = SelectField(choices=choices_estate_type)
    description = StringField('description')
    address =StringField('Address')
    square = DecimalField('square')
    submit = SubmitField('Submit')
    
class SelectForm(FlaskForm):
    choices_estate_type = [
        ('Biệt thự', 'Biệt thự'),
        ('Biệt thự liền kề', 'Biệt thự liền kề'),
        ('Chung cư', 'Chung cư'),
        ('Các loại khác', 'Các loại khác'),
        ('Kho xưởng', 'Kho xưởng'),
        ('Mặt bằng', 'Mặt bằng'),
        ('Mặt bằng, cửa hàng', 'Mặt bằng, cửa hàng'),
        ('Nhà hàng, khách sạn', 'Nhà hàng, khách sạn'),
        ('Nhà mặt tiền', 'Nhà mặt tiền'),
        ('Nhà ngõ, hẻm', 'Nhà ngõ, hẻm'),
        ('Nhà phố', 'Nhà phố'),
        ('Nhà riêng', 'Nhà riêng'),
        ('Nhà xưởng', 'Nhà xưởng'),
        ('Nhà đất', 'Nhà đất'),
        ('Phòng trọ, nhà trọ', 'Phòng trọ, nhà trọ'),
        ('Shop, kiot, quán', 'Shop, kiot, quán'),
        ('Trang trại', 'Trang trại'),
        ('Trang trại khu nghỉ dưỡng', 'Trang trại khu nghỉ dưỡng'),
        ('Văn phòng', 'Văn phòng'),
        ('Đất', 'Đất'),
        ('Đất nông, lâm nghiệp', 'Đất nông, lâm nghiệp'),
        ('Đất nền dự án', 'Đất nền dự án'),
        ('Đất nền, phân lô', 'Đất nền, phân lô')
    
    ]
    choice_district=[
        ('Ba Đình', 'Ba Đình'),
        ('Hoàn Kiếm', 'Hoàn Kiếm'),
        ('Tây Hồ', 'Tây Hồ'),
        ('Long Biên', 'Long Biên'),
        ('Cầu Giấy', 'Cầu Giấy'),
        ('Đống Đa', 'Đống Đa'),
        ('Hai Bà Trưng', 'Hai Bà Trưng'),
        ('Hoàng Mai', 'Hoàng Mai'),
        ('Thanh Xuân', 'Thanh Xuân'),
        ('Hà Đông', 'Hà Đông'),
        ('Bắc Từ Liêm', 'Bắc Từ Liêm'),
        ('Nam Từ Liêm', 'Nam Từ Liêm'),
        ('Sơn Tây', 'Sơn Tây'),
        ('Ba Vì', 'Ba Vì'),
        ('Chương Mỹ', 'Chương Mỹ'),
        ('Đan Phượng', 'Đan Phượng'),
        ('Đông Anh', 'Đông Anh'),
        ('Gia Lâm', 'Gia Lâm'),
        ('Hoài Đức', 'Hoài Đức'),
        ('Mê Linh', 'Mê Linh'),
        ('Mỹ Đức', 'Mỹ Đức'),
        ('Phú Xuyên', 'Phú Xuyên'),
        ('Phúc Thọ', 'Phúc Thọ'),
        ('Quốc Oai', 'Quốc Oai'),
        ('Sóc Sơn', 'Sóc Sơn'),
        ('Thạch Thất', 'Thạch Thất'),
        ('Thanh Oai', 'Thanh Oai'),
        ('Thanh Trì', 'Thanh Trì'),
        ('Thường Tín', 'Thường Tín'),
        ('Ứng Hòa', 'Ứng Hòa'),
    ]
    choice_district_2=[
        ('Hoàn Kiếm', 'Hoàn Kiếm'),
        ('Hai Bà Trưng', 'Hai Bà Trưng'),
        ('Hà Đông', 'Hà Đông'),
    ]
    data_estate_type1=SelectMultipleField('Select Options', choices=choices_estate_type,option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    data_estate_type2=SelectMultipleField('Select Options', choices=choices_estate_type,option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    districts =SelectMultipleField('Select Options', choices=choice_district,option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    submit = SubmitField('Submit')