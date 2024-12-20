#   today = datetime.today()
#     six_months_ago = today - timedelta(days=180)

#     sales_data = db.session.query(
#         func.date_format(Order.created_at, '%Y-%m').label('month'),
#         func.sum(Order.total_amount).label('total_sales')
#     ).filter(Order.created_at >= six_months_ago).group_by(func.date_format(Order.created_at, '%Y-%m')).order_by(func.date_format(Order.created_at, '%Y-%m')).all()

    today = datetime.today()
    six_months_ago = today - timedelta(days=180)

    sales_data = db.session.query(
        func.to_char(Order.created_at, 'YYYY-MM').label('month'),
        func.sum(Order.total_amount).label('total_sales')
    ).filter(Order.created_at >= six_months_ago).group_by(func.to_char(Order.created_at, 'YYYY-MM')).order_by(func.to_char(Order.created_at, 'YYYY-MM')).all()

alembic version no
# c24d797285bI