


class Uploader:

    def upload_image_to_product(instance, filename):

        return f"products/{instance.product.name}/{filename}"
    
    def upload_image_of_user(instance, filename):
        return f"accounts/{instance.product.name}/{filename}"