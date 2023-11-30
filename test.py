from werkzeug.datastructures import ImmutableMultiDict

data = ImmutableMultiDict([('ID', ''), ('Name', 'sfg'), ('Email', 'fdg'), ('Password', 'dfg'), ('Gender', 'dg'), ('Age', '12'), ('Membership', ''), ('undefined', '')])

# Keys you want to retrieve dynamically
# keys_to_fetch = ['Name', 'Email']

# Fetch values for the specified keys dynamically
values = {key: data.get(key, '') for key in data}

# Print the values
for key, value in values.items():
    print(f"{key}: {value}")
