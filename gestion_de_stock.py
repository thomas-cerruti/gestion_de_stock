import tkinter as tk
from tkinter import ttk, simpledialog
import mysql.connector

class StockManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock")

        # Connexion à la base de données
        self.db = mysql.connector.connect(
            host="localhost",
            user='root',
            password='elea',
            database='store',
        )
        self.cursor = self.db.cursor()

        # Création de l'interface graphique
        self.create_gui()

    def create_gui(self):
        # Création du tableau de bord
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Nom', 'Description', 'Prix', 'Quantité', 'Catégorie'))
        self.tree.heading('#1', text='ID')
        self.tree.heading('#2', text='Nom')
        self.tree.heading('#3', text='Description')
        self.tree.heading('#4', text='Prix')
        self.tree.heading('#5', text='Quantité')
        self.tree.heading('#6', text='Catégorie')

        # Ajout des boutons pour gérer les produits
        add_button = tk.Button(self.root, text="Ajouter Produit", command=self.add_product)
        delete_button = tk.Button(self.root, text="Supprimer Produit", command=self.delete_product)
        edit_button = tk.Button(self.root, text="Modifier Produit", command=self.edit_product)

        # Placement des éléments dans la fenêtre
        self.tree.pack(padx=10, pady=10)
        add_button.pack(pady=5)
        delete_button.pack(pady=5)
        edit_button.pack(pady=5)

        # Charger les données de la base de données
        self.load_data()

    def load_data(self):
        # Effacer les éléments existants dans le tableau de bord
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sélectionner tous les produits de la base de données
        query = "SELECT product.id, product.name, product.description, product.price, product.quantity, category.name " \
                "FROM product JOIN category ON product.id_category = category.id"
        self.cursor.execute(query)
        products = self.cursor.fetchall()

        # Ajouter les produits au tableau de bord
        for product in products:
            self.tree.insert('', 'end', values=product)

    def add_product(self):
        # Fonction pour ajouter un nouveau produit
        add_dialog = tk.Toplevel(self.root)
        add_dialog.title("Ajouter Produit")

        product_name = simpledialog.askstring("Ajouter Produit", "Nom du produit:")
        product_description = simpledialog.askstring("Ajouter Produit", "Description du produit:")
        product_price = simpledialog.askinteger("Ajouter Produit", "Prix du produit:")
        product_quantity = simpledialog.askinteger("Ajouter Produit", "Quantité du produit:")

        # Obtenez la liste des catégories depuis la base de données
        category_query = "SELECT name FROM category"
        self.cursor.execute(category_query)
        categories = [category[0] for category in self.cursor.fetchall()]

        # Créez une liste déroulante pour les catégories
        category_label = tk.Label(add_dialog, text="Catégorie du produit:")
        category_combobox = ttk.Combobox(add_dialog, values=categories)
        category_combobox.set(categories[0])

        # Afficher la boîte de dialogue pour ajouter un produit
        def add_product_to_db():
            nonlocal category_combobox
            product_category = category_combobox.get()

            # Ajouter le nouveau produit à la base de données
            query = "INSERT INTO product (name, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, " \
                    "(SELECT id FROM category WHERE name = %s))"
            values = (product_name, product_description, product_price, product_quantity, product_category)

            try:
                self.cursor.execute(query, values)
                self.db.commit()
                print("Produit ajouté avec succès!")
                add_dialog.destroy()
                # Recharger les données après l'ajout du produit
                self.load_data()
            except mysql.connector.Error as err:
                print(f"Erreur lors de l'ajout du produit: {err}")

        add_button = tk.Button(add_dialog, text="Ajouter", command=add_product_to_db)

        # Placement des éléments dans la fenêtre
        category_label.pack(pady=5)
        category_combobox.pack(pady=5)
        add_button.pack(pady=10)

    def delete_product(self):
        # Récupérer l'ID du produit sélectionné dans le tableau de bord
        selected_item = self.tree.selection()
        
        if not selected_item:
            print("Veuillez sélectionner un produit à supprimer.")
            return

        # Demander confirmation à l'utilisateur
        confirmation = tk.messagebox.askyesno("Supprimer Produit", "Êtes-vous sûr de vouloir supprimer ce produit ?")

        if confirmation:
            # Récupérer l'ID du produit sélectionné
            product_id = self.tree.item(selected_item, 'values')[0]

            # Supprimer le produit de la base de données
            delete_query = "DELETE FROM product WHERE id = %s"
            self.cursor.execute(delete_query, (product_id,))
            self.db.commit()

            print("Produit supprimé avec succès!")

            # Recharger les données après la suppression du produit
            self.load_data()


    def edit_product(self):
        # Récupérer l'ID du produit sélectionné dans le tableau de bord
        selected_item = self.tree.selection()

        if not selected_item:
            print("Veuillez sélectionner un produit à modifier.")
            return

        # Récupérer les informations actuelles du produit sélectionné
        current_values = self.tree.item(selected_item, 'values')
        current_id, current_name, current_description, current_price, current_quantity, current_category = current_values

        # Créer une boîte de dialogue pour éditer le produit
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Modifier Produit")

        # Champs de saisie pour les nouvelles valeurs
        new_name = tk.Entry(edit_dialog, width=30)
        new_name.insert(0, current_name)

        new_description = tk.Entry(edit_dialog, width=30)
        new_description.insert(0, current_description)

        new_price = tk.Entry(edit_dialog, width=30)
        new_price.insert(0, current_price)

        new_quantity = tk.Entry(edit_dialog, width=30)
        new_quantity.insert(0, current_quantity)

        # Obtenez la liste des catégories depuis la base de données
        category_query = "SELECT name FROM category"
        self.cursor.execute(category_query)
        categories = [category[0] for category in self.cursor.fetchall()]

        # Créez une liste déroulante pour les catégories
        category_label = tk.Label(edit_dialog, text="Catégorie du produit:")
        category_combobox = ttk.Combobox(edit_dialog, values=categories)
        category_combobox.set(current_category)

        # Afficher la boîte de dialogue pour éditer le produit
        def save_changes():
            nonlocal current_id

            # Récupérer les nouvelles valeurs
            new_name_value = new_name.get()
            new_description_value = new_description.get()
            new_price_value = new_price.get()
            new_quantity_value = new_quantity.get()
            new_category_value = category_combobox.get()

            # Mettre à jour le produit dans la base de données
            update_query = "UPDATE product SET name=%s, description=%s, price=%s, quantity=%s, id_category=(SELECT id FROM category WHERE name=%s) WHERE id=%s"
            values = (new_name_value, new_description_value, new_price_value, new_quantity_value, new_category_value, current_id)

            try:
                self.cursor.execute(update_query, values)
                self.db.commit()
                print("Produit modifié avec succès!")
                edit_dialog.destroy()
                # Recharger les données après la modification du produit
                self.load_data()
            except mysql.connector.Error as err:
                print(f"Erreur lors de la modification du produit: {err}")

        save_button = tk.Button(edit_dialog, text="Enregistrer les modifications", command=save_changes)

        # Placement des éléments dans la boîte de dialogue
        new_name.grid(row=0, column=1, pady=5)
        new_description.grid(row=1, column=1, pady=5)
        new_price.grid(row=2, column=1, pady=5)
        new_quantity.grid(row=3, column=1, pady=5)
        category_label.grid(row=4, column=0, pady=5)
        category_combobox.grid(row=4, column=1, pady=5)
        save_button.grid(row=5, column=1, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagerApp(root)
    root.mainloop()
    