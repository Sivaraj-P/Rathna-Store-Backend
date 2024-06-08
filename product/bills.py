import os
from xhtml2pdf import pisa             # import python module

def generate_html_bill(order, order_items):
    """
    Generate HTML bill with order and product details.
    """
    html_content = f"""
    <html>
    <head>
        <title>Order Bill</title>
        <style>
            h1,h4{{
            text-align:center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 4px;
                text-align: left;
            }}
            img {{
                max-width: 70px;
                max-height: 60px;
            }}
            .total {{
                text-align: right;
                padding-right: 10px;
                font-weight: bold;
            }}

        </style>
    </head>
    <body>
        <h1>Rathna Store</h1>
        <h4>Order Bill</h4>
        <p>Order ID: {order.order_id}</p>
        <p>User: {order.user.first_name} {order.user.last_name}</p>
        <p>Shipping Address: {order.shipping_address.address}</p>
        <p>Date: {order.created_at.strftime("%d-%m-%Y %H:%M:%S")}</p>
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in order_items:

        # image_tag = f'<img src="{product.image.path}" alt="{product.name}">' if product.image else ''
        html_content += f"""
            <tr>
                <td>{item.product.name}</td>
                <td>{item.qty}</td>
                <td>{item.price}</td>
                <td>{item.total}
                
            </tr>
        """

    html_content += f"""
            </tbody>
        </table>
                <p class="total">Total Price: {order.total_price}</p>

    </body>
    </html>
    """

    return html_content

def generate_pdf_bill(order, order_items, filename):
    try:
        result_file = open(filename, "w+b")

        pisa_status = pisa.CreatePDF(
                generate_html_bill(order,order_items),                
                dest=result_file)         

      
        result_file.close()
    except Exception as e:
        print("Error when generating pdf bill",e)
    # finally:
    #     if os.path.exists(filename):
    #         os.remove(filename)
                 