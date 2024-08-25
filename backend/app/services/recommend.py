import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.preprocessing import StandardScaler

class LinearRegressionModel(nn.Module):
    def __init__(self, input_size):
        super(LinearRegressionModel, self).__init__()
        self.linear = nn.Linear(input_size, 1)

    def forward(self, x):
        return self.linear(x)

class MusicRecommender:
    def __init__(self, n_neighbors=5):
        self.scaler = StandardScaler()
        self.n_neighbors = n_neighbors
        self.linear_model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def preprocess_tracks(self, tracks):
        features = np.array([[
            track['popularity'],
            track['audio_features']['danceability'],
            track['audio_features']['energy'],
            track['audio_features']['valence'],
            track['audio_features']['tempo']
        ] for track in tracks])
        return self.scaler.fit_transform(features)

    def fit(self, tracks, user_ratings):
        X = self.preprocess_tracks(tracks)
        X = torch.FloatTensor(X).to(self.device)
        y = torch.FloatTensor(user_ratings).unsqueeze(1).to(self.device)

        self.X_train = X
        self.y_train = y

        self.linear_model = LinearRegressionModel(X.shape[1]).to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.linear_model.parameters())

        for epoch in range(1000): 
            optimizer.zero_grad()
            outputs = self.linear_model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()

    def knn_predict(self, X):
        distances = torch.cdist(X, self.X_train)
        _, indices = torch.topk(distances, k=min(self.n_neighbors, self.X_train.size(0)), largest=False, dim=1)
        neighbor_ratings = self.y_train[indices]
        knn_predictions = torch.mean(neighbor_ratings, dim=1)
        return knn_predictions

    def predict(self, new_tracks):
        X = self.preprocess_tracks(new_tracks)
        X = torch.FloatTensor(X).to(self.device)

        knn_scores = self.knn_predict(X)


        self.linear_model.eval()
        with torch.no_grad():
            lr_scores = self.linear_model(X).squeeze()

        combined_scores = 0.5 * knn_scores + 0.5 * lr_scores

        return combined_scores.cpu().numpy().flatten()

recommender = MusicRecommender()