import mysql.connector
from mysql.connector import Error

class ItemDatabase:
    def __init__(self, host, user, password, database):
        """
        初始化数据库连接。
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        建立数据库连接。
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to the database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def close(self):
        """
        关闭数据库连接。
        """
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def insert_item(self, item_data):
        """
        插入一条数据到items表。
        :param item_data: 一个字典，包含所有字段的值。
        """
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO items (class_id, color, size_x, size_y, size_z, date_time, expected_price, deal_price, deal_platform_name, path_pic_01, path_pic_02, path_pic_03, path_pic_04)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                item_data['class_id'],
                item_data['color'],
                item_data['size_x'],
                item_data['size_y'],
                item_data['size_z'],
                item_data['date_time'],
                item_data['expected_price'],
                item_data['deal_price'],
                item_data['deal_platform_name'],
                item_data['path_pic_01'],
                item_data['path_pic_02'],
                item_data['path_pic_03'],
                item_data['path_pic_04']
            ))
            self.connection.commit()
            print("Item inserted successfully")
        except Error as e:
            print(f"Error while inserting item: {e}")

    def query_by_class_id(self, class_id):
        """
        根据class_id查询数据。
        :param class_id: 要查询的class_id。
        :return: 查询结果列表。
        """
        return self._query_by_field("class_id", class_id)

    def query_by_color(self, color):
        """
        根据color查询数据。
        :param color: 要查询的color。
        :return: 查询结果列表。
        """
        return self._query_by_field("color", color)

    def query_by_size(self, size_x_min=None, size_x_max=None, size_y_min=None, size_y_max=None, size_z_min=None, size_z_max=None):
        """
        根据size_x, size_y, size_z的区间范围查询数据。
        :param size_x_min: size_x的最小值。
        :param size_x_max: size_x的最大值。
        :param size_y_min: size_y的最小值。
        :param size_y_max: size_y的最大值。
        :param size_z_min: size_z的最小值。
        :param size_z_max: size_z的最大值。
        :return: 查询结果列表。
        """
        conditions = []
        params = []
        if size_x_min is not None:
            conditions.append("size_x >= %s")
            params.append(size_x_min)
        if size_x_max is not None:
            conditions.append("size_x <= %s")
            params.append(size_x_max)
        if size_y_min is not None:
            conditions.append("size_y >= %s")
            params.append(size_y_min)
        if size_y_max is not None:
            conditions.append("size_y <= %s")
            params.append(size_y_max)
        if size_z_min is not None:
            conditions.append("size_z >= %s")
            params.append(size_z_min)
        if size_z_max is not None:
            conditions.append("size_z <= %s")
            params.append(size_z_max)

        if not conditions:
            return []

        query = f"SELECT * FROM items WHERE {' AND '.join(conditions)}"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error while querying by size: {e}")
            return []

    def query_by_class_id_color_and_size(self, class_id=None, color=None, size_x_min=None, size_x_max=None, size_y_min=None, size_y_max=None, size_z_min=None, size_z_max=None):
        """
        综合查询：根据class_id、color和size_x/y/z的区间范围查询数据。
        :param class_id: 要查询的class_id。
        :param color: 要查询的color。
        :param size_x_min: size_x的最小值。
        :param size_x_max: size_x的最大值。
        :param size_y_min: size_y的最小值。
        :param size_y_max: size_y的最大值。
        :param size_z_min: size_z的最小值。
        :param size_z_max: size_z的最大值。
        :return: 查询结果列表。
        """
        conditions = []
        params = []
        if class_id is not None:
            conditions.append("class_id = %s")
            params.append(class_id)
        if color is not None:
            conditions.append("color = %s")
            params.append(color)
        if size_x_min is not None:
            conditions.append("size_x >= %s")
            params.append(size_x_min)
        if size_x_max is not None:
            conditions.append("size_x <= %s")
            params.append(size_x_max)
        if size_y_min is not None:
            conditions.append("size_y >= %s")
            params.append(size_y_min)
        if size_y_max is not None:
            conditions.append("size_y <= %s")
            params.append(size_y_max)
        if size_z_min is not None:
            conditions.append("size_z >= %s")
            params.append(size_z_min)
        if size_z_max is not None:
            conditions.append("size_z <= %s")
            params.append(size_z_max)

        if not conditions:
            return []

        query = f"SELECT * FROM items WHERE {' AND '.join(conditions)}"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error while querying by class_id, color, and size: {e}")
            return []

    def _query_by_field(self, field, value):
        """
        通用查询方法。
        :param field: 字段名。
        :param value: 字段值。
        :return: 查询结果列表。
        """
        query = f"SELECT * FROM items WHERE {field} = %s"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (value,))
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error while querying by {field}: {e}")
            return []

# 示例使用
if __name__ == "__main__":
    db = ItemDatabase(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )
    db.connect()

    # 插入数据
    item_data = {
        "class_id": 1,
        "color": "red",
        "size_x": 10.5,
        "size_y": 20.5,
        "size_z": 5.5,
        "date_time": "2023-10-01 12:00:00",
        "expected_price": 100.0,
        "deal_price": 90.0,
        "deal_platform_name": "platform1",
        "path_pic_01": "path/to/pic1.jpg",
        "path_pic_02": "path/to/pic2.jpg",
        "path_pic_03": "path/to/pic3.jpg",
        "path_pic_04": "path/to/pic4.jpg"
    }
    db.insert_item(item_data)

    # 综合查询
    print("Query by class_id, color, and size ranges:")
    result = db.query_by_class_id_color_and_size(
        class_id=1,
        color="red",
        size_x_min=10.0,
        size_x_max=11.0,
        size_y_min=20.0,
        size_y_max=21.0,
        size_z_min=5.0,
        size_z_max=6.0
    )
    print(result)

    db.close()
